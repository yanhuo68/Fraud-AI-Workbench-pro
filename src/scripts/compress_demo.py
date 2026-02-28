import os
import zipfile
from pathlib import Path
from PIL import Image

def compress_images():
    base_dir = Path(__file__).parent.parent.parent
    src_dir = base_dir / "documentation" / "screen"
    dest_dir = base_dir / "documentation" / "compressed-screen"
    zip_path = base_dir / "documentation" / "compressed_demo.zip"
    
    if not src_dir.exists():
        print(f"Source directory {src_dir} does not exist.")
        return

    # Create destination directory if it doesn't exist
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Track statistics
    total_original_size = 0
    total_compressed_size = 0
    count = 0

    print("Starting compression...")
    
    # Walk through the source directory
    for root, dirs, files in os.walk(src_dir):
        # Calculate relative path to maintain folder structure
        rel_path = Path(root).relative_to(src_dir)
        curr_dest_dir = dest_dir / rel_path
        
        # Create corresponding directory in destination
        curr_dest_dir.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                src_file = Path(root) / file
                # Save as optimized JPEG to save maximum space, but keep PNG if requested
                # We will convert everything to high-quality JPEG for maximum ratio
                dest_file = curr_dest_dir / (src_file.stem + ".jpg")
                
                original_size = src_file.stat().st_size
                total_original_size += original_size
                
                try:
                    with Image.open(src_file) as img:
                        # Convert to RGB if it's RGBA (PNG with transparency)
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                        
                        # Resize if excessively large (e.g. > 1920 width)
                        max_width = 1920
                        if img.width > max_width:
                            ratio = max_width / img.width
                            new_size = (max_width, int(img.height * ratio))
                            img = img.resize(new_size, Image.Resampling.LANCZOS)
                            
                        # Save with optimization
                        img.save(dest_file, "JPEG", quality=85, optimize=True)
                        
                    compressed_size = dest_file.stat().st_size
                    total_compressed_size += compressed_size
                    count += 1
                    print(f"Compressed {rel_path / file}: {original_size/1024/1024:.1f}MB -> {compressed_size/1024/1024:.2f}MB")
                except Exception as e:
                    print(f"Error compressing {src_file}: {e}")

    print(f"\nCompression complete! Processed {count} images.")
    print(f"Original size: {total_original_size/1024/1024:.1f}MB")
    print(f"Compressed size: {total_compressed_size/1024/1024:.1f}MB")
    print(f"Reduction: {(1 - total_compressed_size/(total_original_size or 1))*100:.1f}%")

    # Now bundle into a ZIP file
    print("\nCreating ZIP bundle...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dest_dir):
            for file in files:
                file_path = Path(root) / file
                # Add to zip with path relative to compressed-screen directory
                arcname = file_path.relative_to(dest_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"ZIP bundle created at: {zip_path}")
    print(f"ZIP size: {zip_path.stat().st_size/1024/1024:.1f}MB")

if __name__ == "__main__":
    compress_images()
