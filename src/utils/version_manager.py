"""
Dataset and Model Version Management System

Provides utilities for managing multiple datasets and trained models,
enabling versioning, comparison, and experimentation.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any
import shutil


def get_est_timestamp() -> str:
    """Return current timestamp in EST (UTC-5)."""
    est = timezone(timedelta(hours=-5))
    return datetime.now(est).isoformat()

class DatasetManager:
    """Manages versioned datasets for LLM fine-tuning."""
    
    def __init__(self, base_path: str = "data/llm/datasets"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.base_path / "metadata.json"
        self._init_metadata()
    
    def _init_metadata(self):
        """Initialize metadata file if it doesn't exist."""
        if not self.metadata_file.exists():
            metadata = {
                "datasets": [],
                "active_dataset": None
            }
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
    
    def _load_metadata(self) -> Dict:
        """Load metadata from file."""
        with open(self.metadata_file, 'r') as f:
            return json.load(f)
    
    def _save_metadata(self, metadata: Dict):
        """Save metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def create_dataset(self, name: str, description: str = "", clone_from: Optional[str] = None) -> str:
        """
        Create a new dataset.
        
        Args:
            name: Dataset name
            description: Optional description
            clone_from: Optional dataset ID to clone from
            
        Returns:
            dataset_id: ID of created dataset
        """
        metadata = self._load_metadata()
        
        # Generate ID from name
        dataset_id = name.lower().replace(' ', '_').replace('-', '_')
        
        # Check if exists
        if any(d['id'] == dataset_id for d in metadata['datasets']):
            raise ValueError(f"Dataset '{dataset_id}' already exists")
        
        # Create directory
        dataset_dir = self.base_path / dataset_id
        dataset_dir.mkdir(exist_ok=True)
        
        # Create info file
        info = {
            "id": dataset_id,
            "name": name,
            "description": description,
            "created": get_est_timestamp(),
            "sample_count": 0,
            "linked_models": []
        }
        
        with open(dataset_dir / "info.json", 'w') as f:
            json.dump(info, f, indent=2)
        
        # Create empty samples file
        samples_file = dataset_dir / "samples.jsonl"
        samples_file.touch()
        
        # Clone if requested
        if clone_from:
            self._clone_samples(clone_from, dataset_id)
            info['sample_count'] = self._count_samples(dataset_id)
            with open(dataset_dir / "info.json", 'w') as f:
                json.dump(info, f, indent=2)
        
        # Update metadata
        metadata['datasets'].append(info)
        if not metadata['active_dataset']:
            metadata['active_dataset'] = dataset_id
        
        self._save_metadata(metadata)
        
        return dataset_id
    
    def get_all_datasets(self) -> List[Dict]:
        """Get list of all datasets."""
        metadata = self._load_metadata()
        return metadata['datasets']
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """Get specific dataset info."""
        datasets = self.get_all_datasets()
        for ds in datasets:
            if ds['id'] == dataset_id:
                return ds
        return None
    
    def get_active_dataset(self) -> Optional[str]:
        """Get ID of active dataset."""
        metadata = self._load_metadata()
        return metadata.get('active_dataset')
    
    def set_active_dataset(self, dataset_id: str):
        """Set active dataset."""
        if not self.get_dataset(dataset_id):
            raise ValueError(f"Dataset '{dataset_id}' not found")
        
        metadata = self._load_metadata()
        metadata['active_dataset'] = dataset_id
        self._save_metadata(metadata)
    
    def delete_dataset(self, dataset_id: str):
        """Delete a dataset."""
        metadata = self._load_metadata()
        
        # Remove from list
        metadata['datasets'] = [d for d in metadata['datasets'] if d['id'] != dataset_id]
        
        # Update active if needed
        if metadata['active_dataset'] == dataset_id:
            metadata['active_dataset'] = metadata['datasets'][0]['id'] if metadata['datasets'] else None
        
        self._save_metadata(metadata)
        
        # Delete directory
        dataset_dir = self.base_path / dataset_id
        if dataset_dir.exists():
            shutil.rmtree(dataset_dir)
    
    def get_samples(self, dataset_id: str) -> List[Dict]:
        """Load all samples from dataset."""
        samples_file = self.base_path / dataset_id / "samples.jsonl"
        if not samples_file.exists():
            return []
        
        samples = []
        with open(samples_file, 'r') as f:
            for line in f:
                if line.strip():
                    samples.append(json.loads(line))
        return samples
    
    def add_sample(self, dataset_id: str, sample: Dict):
        """Add a sample to dataset."""
        samples_file = self.base_path / dataset_id / "samples.jsonl"
        
        with open(samples_file, 'a') as f:
            f.write(json.dumps(sample) + '\n')
        
        # Update count
        self._update_sample_count(dataset_id)
    
    def delete_sample(self, dataset_id: str, sample_index: int):
        """Delete a sample by index."""
        samples = self.get_samples(dataset_id)
        if 0 <= sample_index < len(samples):
            del samples[sample_index]
            self._save_samples(dataset_id, samples)
            self._update_sample_count(dataset_id)
    
    def update_sample(self, dataset_id: str, sample_index: int, updated_sample: Dict):
        """Update a sample."""
        samples = self.get_samples(dataset_id)
        if 0 <= sample_index < len(samples):
            samples[sample_index] = updated_sample
            self._save_samples(dataset_id, samples)
    
    def _save_samples(self, dataset_id: str, samples: List[Dict]):
        """Save samples to file."""
        samples_file = self.base_path / dataset_id / "samples.jsonl"
        with open(samples_file, 'w') as f:
            for sample in samples:
                f.write(json.dumps(sample) + '\n')
    
    def _count_samples(self, dataset_id: str) -> int:
        """Count samples in dataset."""
        return len(self.get_samples(dataset_id))
    
    def _update_sample_count(self, dataset_id: str):
        """Update sample count in metadata."""
        count = self._count_samples(dataset_id)
        
        # Update info.json
        info_file = self.base_path / dataset_id / "info.json"
        with open(info_file, 'r') as f:
            info = json.load(f)
        info['sample_count'] = count
        with open(info_file, 'w') as f:
            json.dump(info, f, indent=2)
        
        # Update metadata
        metadata = self._load_metadata()
        for ds in metadata['datasets']:
            if ds['id'] == dataset_id:
                ds['sample_count'] = count
                break
        self._save_metadata(metadata)
    
    def _clone_samples(self, source_id: str, target_id: str):
        """Clone samples from one dataset to another."""
        samples = self.get_samples(source_id)
        for sample in samples:
            self.add_sample(target_id, sample)


class ModelManager:
    """Manages versioned trained models."""
    
    def __init__(self, base_path: str = "models"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.base_path / "registry.json"
        self._init_registry()
    
    def _init_registry(self):
        """Initialize registry file if it doesn't exist."""
        if not self.registry_file.exists():
            registry = {
                "models": []
            }
            with open(self.registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
    
    def _load_registry(self) -> Dict:
        """Load registry from file."""
        with open(self.registry_file, 'r') as f:
            return json.load(f)
    
    def _save_registry(self, registry: Dict):
        """Save registry to file."""
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def register_model(self, name: str, dataset_id: str, training_params: Dict, 
                      metrics: Optional[Dict] = None) -> str:
        """
        Register a new trained model.
        
        Args:
            name: Model name
            dataset_id: Dataset used for training
            training_params: Training configuration
            metrics: Optional training metrics
            
        Returns:
            model_id: ID of registered model
        """
        registry = self._load_registry()
        
        # Generate ID
        model_id = name.lower().replace(' ', '_').replace('-', '_')
        
        # Check if exists
        if any(m['id'] == model_id for m in registry['models']):
            raise ValueError(f"Model '{model_id}' already exists")
        
        # Create directory
        model_dir = self.base_path / model_id
        model_dir.mkdir(exist_ok=True)
        
        # Create config
        config = {
            "id": model_id,
            "name": name,
            "dataset_id": dataset_id,
            "created": get_est_timestamp(),
            "training_params": training_params,
            "metrics": metrics or {}
        }
        
        with open(model_dir / "config.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        # Update registry
        registry['models'].append(config)
        self._save_registry(registry)
        
        return model_id
    
    def get_all_models(self) -> List[Dict]:
        """Get list of all models."""
        registry = self._load_registry()
        return registry['models']
    
    def get_model(self, model_id: str) -> Optional[Dict]:
        """Get specific model info."""
        models = self.get_all_models()
        for m in models:
            if m['id'] == model_id:
                return m
        return None
    
    def get_models_by_dataset(self, dataset_id: str) -> List[Dict]:
        """Get all models trained on a specific dataset."""
        models = self.get_all_models()
        return [m for m in models if m['dataset_id'] == dataset_id]
    
    def delete_model(self, model_id: str):
        """Delete a model."""
        registry = self._load_registry()
        
        # Remove from registry
        registry['models'] = [m for m in registry['models'] if m['id'] != model_id]
        self._save_registry(registry)
        
        # Delete directory
        model_dir = self.base_path / model_id
        if model_dir.exists():
            shutil.rmtree(model_dir)
    
    def get_model_path(self, model_id: str) -> Path:
        """Get the directory path for a model."""
        return self.base_path / model_id / "adapters"
