import os
import requests
import time
import glob

# --- Configuration ---
# Directory where the txt files are located (current directory by default)
# Update this to point to the yoga_dataset_links directory
TXT_FILES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Yoga-82", "yoga_dataset_links")
DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Yoga-82", "dataset")
# Files to exclude from processing (not containing URLs)
EXCLUDE_FILES = ["yoga_train.txt", "yoga_test.txt", "ReadMe.txt", os.path.basename(__file__)]
# Delay between requests (in seconds) to avoid overwhelming servers
DOWNLOAD_DELAY = 0.1
# Timeout for each download request (in seconds)
REQUEST_TIMEOUT = 15
# --- End Configuration ---

def download_image(url, save_path):
    """Downloads an image from a URL and saves it to the specified path."""
    try:
        # Create the directory if it doesn't exist
        directory = os.path.dirname(save_path)
        if directory and not os.path.exists(directory):
            print(f"    Creating directory: {directory}")
            os.makedirs(directory)

        # Check if file already exists
        if os.path.exists(save_path):
            print(f"    Skipping (already exists): {save_path}")
            return True

        print(f"    Downloading: {url} -> {save_path}")
        response = requests.get(url, stream=True, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Save the image
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True

    except requests.exceptions.RequestException as e:
        print(f"    Error downloading {url}: {e}")
    except Exception as e:
        print(f"    An unexpected error occurred for {url}: {e}")
    return False

def process_pose_file(filepath):
    """Reads a pose file, extracts URLs, and downloads images."""
    print(f"\nProcessing file: {os.path.basename(filepath)}...")
    download_count = 0
    error_count = 0
    skipped_count = 0
    total_lines = 0

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            total_lines = len(lines)
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                # Split by tab character (which is used in Yoga-82 dataset)
                parts = line.split('\t')
                if len(parts) == 2:
                    relative_image_path = parts[0].strip()
                    url = parts[1].strip()

                    # Construct the full save path relative to the dataset directory
                    save_path = os.path.join(DATASET_DIR, relative_image_path)

                    # Handle potential Windows vs Linux path separators in the relative path
                    save_path = os.path.normpath(save_path)

                    # Check if file exists before attempting download to count skips accurately
                    if os.path.exists(save_path):
                        print(f"  [{i+1}/{total_lines}] Skipping (already exists): {save_path}")
                        skipped_count += 1
                        continue

                    if download_image(url, save_path):
                        download_count += 1
                    else:
                        error_count += 1

                    time.sleep(DOWNLOAD_DELAY) # Be polite to the server
                else:
                    print(f"    Warning: Skipping malformed line in {os.path.basename(filepath)}: {line}")
                    error_count += 1 # Count malformed lines as errors

    except FileNotFoundError:
        print(f"  Error: File not found - {filepath}")
        return 0, 1 , 0 # downloads, errors, skipped
    except Exception as e:
        print(f"  Error processing file {filepath}: {e}")
        return 0, 1, 0 # downloads, errors, skipped

    print(f"  Finished {os.path.basename(filepath)}: {download_count} downloaded, {error_count} errors, {skipped_count} skipped.")
    return download_count, error_count, skipped_count

def main():
    """Main function to find pose files and process them."""
    start_time = time.time()
    
    # Make sure the dataset directory exists
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    # Find all txt files in the yoga_dataset_links directory
    all_txt_files = glob.glob(os.path.join(TXT_FILES_DIR, "*.txt"))

    pose_files_to_process = [
        f for f in all_txt_files if os.path.basename(f) not in EXCLUDE_FILES
    ]

    print(f"Found {len(pose_files_to_process)} pose files to process.")
    print(f"TXT_FILES_DIR: {TXT_FILES_DIR}")
    print(f"DATASET_DIR: {DATASET_DIR}")
    
    if not pose_files_to_process:
        print(f"Error: No pose-specific .txt files found in '{TXT_FILES_DIR}'.")
        print("Please ensure the 82 pose text files are in the same directory as this script.")
        return

    total_downloaded = 0
    total_errors = 0
    total_skipped = 0

    for pose_file in pose_files_to_process:
        downloaded, errors, skipped = process_pose_file(pose_file)
        total_downloaded += downloaded
        total_errors += errors
        total_skipped += skipped

    end_time = time.time()
    duration = end_time - start_time

    print("\n" + "="*30)
    print("Download Summary:")
    print(f"  Processed {len(pose_files_to_process)} files.")
    print(f"  Successfully downloaded: {total_downloaded} images.")
    print(f"  Skipped (already existed): {total_skipped} images.")
    print(f"  Errors / Malformed lines: {total_errors}")
    print(f"  Total duration: {duration:.2f} seconds")
    print("="*30)

if __name__ == "__main__":
    main()