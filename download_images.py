import os
import requests
import glob
from pathlib import Path
import time
import concurrent.futures
from tqdm import tqdm

def download_image(url, save_path):
    """Download an image from url and save it to save_path"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def process_pose_file(pose_file, dataset_dir):
    """Process a single pose file and download all its images"""
    
    with open(pose_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    successful = 0
    failed = 0
    
    pose_name = os.path.basename(pose_file).replace('.txt', '')
    print(f"Processing {pose_name}, found {len(lines)} images")
    
    for line in lines:
        # Split by tab character which separates filename and URL
        parts = line.strip().split('\t')
        if len(parts) != 2:
            print(f"Invalid line format: {line}")
            failed += 1
            continue
        
        rel_path, url = parts
        
        # Create the full save path
        save_path = os.path.join(dataset_dir, rel_path)
        
        # Skip if already downloaded
        if os.path.exists(save_path):
            successful += 1
            continue
        
        # Download the image
        if download_image(url, save_path):
            successful += 1
        else:
            failed += 1
            
    return successful, failed

def main():
    # Base directory for the dataset
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(base_dir, "Yoga-82", "dataset")
    os.makedirs(dataset_dir, exist_ok=True)
    
    # Find all pose text files
    pose_files_pattern = os.path.join(base_dir, "Yoga-82", "yoga_dataset_links", "*.txt")
    pose_files = glob.glob(pose_files_pattern)
    
    if not pose_files:
        print(f"No pose files found at {pose_files_pattern}")
        return
    
    print(f"Found {len(pose_files)} pose files")
    
    total_successful = 0
    total_failed = 0
    
    # Process each pose file
    for pose_file in tqdm(pose_files):
        successful, failed = process_pose_file(pose_file, dataset_dir)
        total_successful += successful
        total_failed += failed
    
    print(f"Download complete. Successfully downloaded {total_successful} images, failed {total_failed}")

if __name__ == "__main__":
    main()