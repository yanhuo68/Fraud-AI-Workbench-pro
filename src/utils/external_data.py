
import os
import requests
import zipfile
import shutil
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)

def download_kaggle_dataset(dataset_slug, download_path="data/uploads", media_path="data/mediauploads"):
    """
    Download a Kaggle dataset using the Kaggle API.
    
    Args:
        dataset_slug (str): Kaggle dataset slug (e.g., 'titanic/titanic-dataset')
        download_path (str): Path to save structured data (csv, json, xml, sql)
        media_path (str): Path to save multimodal data (images, audio, video)
        
    Returns:
        dict: Status and list of downloaded files
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        # Helper to ensure auth is set from environment if passed dynamically
        if not os.environ.get("KAGGLE_USERNAME") or not os.environ.get("KAGGLE_KEY"):
            return {"success": False, "error": "Kaggle credentials missing (KAGGLE_USERNAME, KAGGLE_KEY)."}
            
        api = KaggleApi()
        api.authenticate()
        
        # specific directory for temp extraction
        temp_dir = Path("data/temp_kaggle")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Downloading Kaggle dataset: {dataset_slug}")
        # Download and unzip
        api.dataset_download_files(dataset_slug, path=temp_dir, unzip=True)
        
        downloaded_files = []
        structured_exts = {'.csv', '.xml', '.json', '.sql', '.txt', '.pdf', '.md'}
        media_exts = {'.mp3', '.wav', '.mp4', '.mov', '.avi', '.jpg', '.jpeg', '.png', '.webp', '.mkv'}
        
        Path(download_path).mkdir(parents=True, exist_ok=True)
        Path(media_path).mkdir(parents=True, exist_ok=True)
        
        # Walk and move relevant files
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                src_file = Path(root) / file
                ext = src_file.suffix.lower()
                
                # Determine destination based on file type
                if ext in media_exts:
                    dest_dir = media_path
                else:
                    # Default to structured uploads for everything else (or ignore?)
                    # User asked for "csv, xml or json" specifically, but let's be permissive and put them in uploads
                    # Filter?
                    if ext in structured_exts:
                        dest_dir = download_path
                    else:
                        continue # Skip unknown files like .gitkeep or bins?
                
                dest_file = Path(dest_dir) / file
                # Handle overwrite or rename? Overwrite for now as it's a download action
                shutil.move(str(src_file), str(dest_file))
                downloaded_files.append(str(dest_file))
                
        # Cleanup
        shutil.rmtree(temp_dir)
        
        if not downloaded_files:
             return {"success": False, "error": "No relevant files (CSV, JSON, XML, Media) found in dataset."}
             
        return {"success": True, "files": [str(f) for f in downloaded_files]}
        
    except ImportError:
        return {"success": False, "error": "kaggle library not installed. Please install it."}
    except Exception as e:
        logger.error(f"Kaggle download error: {e}")
        return {"success": False, "error": str(e)}

def download_github_repo(repo_url, branch="main", download_path="data/uploads", media_path="data/mediauploads"):
    """
    Download relevant files from a GitHub repository ZIP.
    
    Args:
        repo_url (str): GitHub repo URL
        branch (str): Branch name (default: main)
    """
    try:
        # Extract owner/repo from URL
        # formats: https://github.com/owner/repo or just owner/repo
        if "github.com" in repo_url:
            parts = repo_url.rstrip("/").split("/")
            if len(parts) >= 2:
                owner, repo = parts[-2], parts[-1]
        else:
            parts = repo_url.split("/")
            if len(parts) == 2:
                owner, repo = parts[0], parts[1]
            else:
                 return {"success": False, "error": "Invalid GitHub URL format."}
        
        # Construct Zipball URL
        zip_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
        
        headers = {}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"
            
        logger.info(f"Downloading GitHub repo: {owner}/{repo}")
        resp = requests.get(zip_url, headers=headers, stream=True)
        
        if resp.status_code != 200:
             return {"success": False, "error": f"GitHub API Error: {resp.status_code} - {resp.text}"}
             
        # Save Zip
        temp_dir = Path("data/temp_github")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        zip_path = temp_dir / "repo.zip"
        with open(zip_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                
        # Extract
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile:
            return {"success": False, "error": "Downloaded file is not a valid zip archive."}
            
        # Move files
        downloaded_files = []
        structured_exts = {'.csv', '.xml', '.json', '.sql', '.txt', '.pdf', '.md'}
        media_exts = {'.mp3', '.wav', '.mp4', '.mov', '.avi', '.jgp', '.jpeg', '.png', '.webp', '.mkv'}
        
        Path(download_path).mkdir(parents=True, exist_ok=True)
        Path(media_path).mkdir(parents=True, exist_ok=True)
        
        # Find the root folder (GitHub zips usually have a root folder)
        root_folder = next((p for p in temp_dir.iterdir() if p.is_dir()), temp_dir)
        
        for root, dirs, files in os.walk(root_folder):
            for file in files:
                src_file = Path(root) / file
                ext = src_file.suffix.lower()
                
                if ext in media_exts:
                    dest_dir = media_path
                elif ext in structured_exts:
                    dest_dir = download_path
                else:
                    continue
                    
                dest_file = Path(dest_dir) / file
                shutil.move(str(src_file), str(dest_file))
                downloaded_files.append(str(dest_file))
                
        # Cleanup
        shutil.rmtree(temp_dir)
        
        if not downloaded_files:
             return {"success": False, "error": "No relevant files found in repository."}
             
        return {"success": True, "files": [str(f) for f in downloaded_files]}

    except Exception as e:
        logger.error(f"GitHub download error: {e}")
        return {"success": False, "error": str(e)}
