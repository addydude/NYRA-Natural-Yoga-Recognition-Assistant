import os
import glob
import shutil
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Base directory configurations
OUTPUT_DIR = os.path.join(r"D:\NYRAGGbackup - Copy\yoga_cnn", "processed_dataset")
TRAIN_DIR = os.path.join(OUTPUT_DIR, 'train')
VAL_DIR = os.path.join(OUTPUT_DIR, 'val')

def is_valid_image(file_path):
    """
    Check if an image file is valid by attempting to open it with PIL.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        bool: True if valid image, False otherwise
    """
    try:
        with Image.open(file_path) as img:
            # Verify the image by loading it
            img.verify()
        # Try to load it again to check if it can be processed
        with Image.open(file_path) as img:
            img.load()
        return True
    except Exception as e:
        return False

def process_folder(folder_path):
    """
    Process all image files in a folder to identify corrupted ones.
    
    Args:
        folder_path: Path to the folder containing images
        
    Returns:
        tuple: (folder_path, valid_count, invalid_files)
    """
    valid_count = 0
    invalid_files = []
    
    # Find all image files
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif']:
        image_files.extend(glob.glob(os.path.join(folder_path, ext)))
    
    if not image_files:
        return folder_path, 0, []
    
    for file_path in image_files:
        if is_valid_image(file_path):
            valid_count += 1
        else:
            invalid_files.append(file_path)
    
    return folder_path, valid_count, invalid_files

def clean_corrupted_images():
    """
    Identify and remove corrupted images from the dataset.
    """
    print("Checking for corrupted images in the dataset...")
    
    # Find all class directories
    class_dirs = []
    for root_dir in [TRAIN_DIR, VAL_DIR]:
        if os.path.exists(root_dir):
            class_dirs.extend([os.path.join(root_dir, d) for d in os.listdir(root_dir) 
                              if os.path.isdir(os.path.join(root_dir, d))])
    
    if not class_dirs:
        print("No class directories found.")
        return
    
    # Process each folder with multithreading
    all_invalid_files = []
    total_images = 0
    total_valid = 0
    
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        # Submit all tasks
        future_to_folder = {executor.submit(process_folder, folder): folder for folder in class_dirs}
        
        # Process results as they complete with a progress bar
        for future in tqdm(as_completed(future_to_folder), total=len(future_to_folder), desc="Checking folders"):
            folder = future_to_folder[future]
            folder_path, valid_count, invalid_files = future.result()
            
            if invalid_files:
                all_invalid_files.extend(invalid_files)
                class_name = os.path.basename(folder_path)
                print(f"Found {len(invalid_files)} corrupted images in {class_name}")
            
            total_valid += valid_count
            total_images += valid_count + len(invalid_files)
    
    # Report results
    print("\nDataset check complete:")
    print(f"Total images: {total_images}")
    print(f"Valid images: {total_valid}")
    print(f"Corrupted images: {len(all_invalid_files)}")
    
    if all_invalid_files:
        print("\nCorrupted image paths:")
        for file_path in all_invalid_files[:10]:  # Show only first 10 to avoid cluttering output
            print(f" - {file_path}")
            
        if len(all_invalid_files) > 10:
            print(f" - ... and {len(all_invalid_files) - 10} more")
        
        # Create a corrupted folder to move files to
        corrupted_dir = os.path.join(OUTPUT_DIR, 'corrupted')
        os.makedirs(corrupted_dir, exist_ok=True)
        
        # Ask if user wants to remove corrupted files
        user_input = input("\nDo you want to remove these corrupted images? (y/n): ")
        if user_input.lower() == 'y':
            for file_path in all_invalid_files:
                try:
                    # Create subdirectory for the class if needed
                    class_name = os.path.basename(os.path.dirname(file_path))
                    class_corrupted_dir = os.path.join(corrupted_dir, class_name)
                    os.makedirs(class_corrupted_dir, exist_ok=True)
                    
                    # Move the file instead of deleting it
                    dest_path = os.path.join(class_corrupted_dir, os.path.basename(file_path))
                    shutil.move(file_path, dest_path)
                except Exception as e:
                    print(f"Error moving {file_path}: {e}")
            
            print(f"\nMoved {len(all_invalid_files)} corrupted images to {corrupted_dir}")
            return True
        else:
            print("No files were removed. Please fix the corrupted images manually.")
            return False
    else:
        print("\nNo corrupted images found! Your dataset is clean.")
        return True

if __name__ == "__main__":
    clean_corrupted_images()