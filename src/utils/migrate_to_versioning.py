"""
Migration script to move existing data to versioned structure.

Migrates:
- data/llm/finetune_dataset.jsonl -> datasets/v1_default/samples.jsonl
- ./adapters/ -> models/model_v1_default/adapters/
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.version_manager import DatasetManager, ModelManager


def migrate_existing_data():
    """Migrate existing dataset and model to versioned structure."""
    
    print("🔄 Starting migration...")
    
    # Initialize managers
    dataset_mgr = DatasetManager()
    model_mgr = ModelManager()
    
    # Check if old dataset exists
    old_dataset = Path("data/llm/finetune_dataset.jsonl")
    
    if old_dataset.exists():
        print(f"\n📦 Found existing dataset: {old_dataset}")
        
        # Create v1_default dataset
        try:
            dataset_id = dataset_mgr.create_dataset(
                name="Default Dataset",
                description="Initial fraud detection dataset (migrated from finetune_dataset.jsonl)"
            )
            print(f"✅ Created dataset: {dataset_id}")
        except ValueError as e:
            print(f"⚠️  Dataset already exists: {e}")
            dataset_id = "default_dataset"
        
        # Copy samples
        print("📝 Copying samples...")
        sample_count = 0
        with open(old_dataset, 'r') as f:
            for line in f:
                if line.strip():
                    sample = json.loads(line)
                    dataset_mgr.add_sample(dataset_id, sample)
                    sample_count += 1
        
        print(f"✅ Migrated {sample_count} samples")
        
        # Backup old file
        backup_path = old_dataset.parent / f"finetune_dataset_backup_{datetime.now().strftime('%Y%m%d')}.jsonl"
        shutil.copy(old_dataset, backup_path)
        print(f"💾 Backed up to: {backup_path}")
        
    else:
        print("⚠️  No existing dataset found at data/llm/finetune_dataset.jsonl")
        # Create empty default dataset
        try:
            dataset_id = dataset_mgr.create_dataset(
                name="Default Dataset",
                description="Default fraud detection dataset"
            )
            print(f"✅ Created empty dataset: {dataset_id}")
        except ValueError:
            print("⚠️  Default dataset already exists")
            dataset_id = "default_dataset"
    
    # Check if old model exists
    old_model = Path("adapters")
    
    if old_model.exists() and old_model.is_dir():
        print(f"\n🤖 Found existing model: {old_model}")
        
        # Register model
        try:
            model_id = model_mgr.register_model(
                name="Default Model",
                dataset_id=dataset_id,
                training_params={
                    "epochs": 3,
                    "iterations": 300,
                    "base_model": "mlx-community/Llama-3.2-1B-Instruct-4bit"
                },
                metrics={
                    "migrated": True,
                    "original_path": str(old_model)
                }
            )
            print(f"✅ Registered model: {model_id}")
        except ValueError as e:
            print(f"⚠️  Model already exists: {e}")
            model_id = "default_model"
        
        # Move model files
        new_model_path = Path("models") / model_id / "adapters"
        new_model_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not new_model_path.exists():
            print(f"📂 Moving model files...")
            shutil.copytree(old_model, new_model_path)
            print(f"✅ Moved to: {new_model_path}")
            
            # Backup original
            backup_model = Path(f"adapters_backup_{datetime.now().strftime('%Y%m%d')}")
            shutil.move(old_model, backup_model)
            print(f"💾 Backed up original to: {backup_model}")
        else:
            print(f"⚠️  Model already exists at: {new_model_path}")
    else:
        print("⚠️  No existing model found at ./adapters/")
    
    print("\n✅ Migration complete!")
    print(f"\n📊 Summary:")
    print(f"   Datasets: {len(dataset_mgr.get_all_datasets())}")
    print(f"   Models: {len(model_mgr.get_all_models())}")
    print(f"   Active dataset: {dataset_mgr.get_active_dataset()}")


if __name__ == "__main__":
    migrate_existing_data()
