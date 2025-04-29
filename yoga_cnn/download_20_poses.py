import os
import requests
import time
import glob
from pathlib import Path
import tqdm
import threading
from queue import Queue

# --- Configuration ---
# Base directories
YOGA82_DIR = r"D:\NYRAGGbackup - Copy\Yoga-82"
DATASET_DIR = os.path.join(YOGA82_DIR, "dataset")
TXT_FILES_DIR = os.path.join(YOGA82_DIR, "yoga_dataset_links")

# Request settings
REQUEST_TIMEOUT = 15
NUM_THREADS = 5
# --- End Configuration ---

# Define the 20 specific poses we want to download
TARGET_POSES = [
    'Child_Pose_or_Balasana_',                         # Balasana
    'Tree_Pose_or_Vrksasana_',                         # Vrksasana
    'Downward-Facing_Dog_pose_or_Adho_Mukha_Svanasana',# Adho Mukha
    'Warrior_I_Pose_or_Virabhadrasana_I',              # Virabhadrasana I
    'Warrior_II_Pose_or_Virabhadrasana_II',            # Virabhadrasana II
    'Chair_Pose_or_Utkatasana_',                       # Utkatasana
    'Cobra_Pose_or_Bhujangasana',                      # Bhujangasana
    'Bridge_Pose_or_Setu_Bandh',                       # Setu Bandha
    'Boat_Pose_or_Paripurna_Na',                       # Navasana
    'Camel_Pose_or_Ustrasana_',                        # Ustrasana
    'Cat_Cow_Pose_or_Marjaryas',                       # Marjaryasana
    'Bound_Angle_Pose_or_Baddh',                       # Baddha Konasana
    'Standing_Forward_Bend_pos',                       # Uttanasana
    'Side_Plank_Pose_or_Vasist',                       # Vasisthasana
    'Plank_Pose_or_Kumbhakasan',                       # Kumbhakasana
    'Seated_Forward_Bend_pose_',                       # Paschimottanasana
    'Upward_Bow_(Wheel)_Pose_o',                       # Urdhva Dhanurasana
    'Corpse_Pose_or_Savasana_',                        # Savasana
    'Dolphin_Pose_or_Ardha_Pin',                       # Ardha Pincha Mayurasana
    'Happy_Baby_Pose_or_Ananda'                        # Ananda Balasana
]

# Global counter for statistics
stats = {
    'downloaded': 0,
    'skipped': 0,
    'errors': 0,
    'total': 0
}

# Lock for thread-safe operations
lock = threading.Lock()

def download_image(url, save_path):
    """Downloads an image from a URL and saves it to the specified path."""
    try:
        # Create the directory if it doesn't exist
        directory = os.path.dirname(save_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # Check if file already exists
        if os.path.exists(save_path):
            with lock:
                stats['skipped'] += 1
            return True

        # Define headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Download the image
        response = requests.get(url, stream=True, timeout=REQUEST_TIMEOUT, headers=headers)
        response.raise_for_status()

        # Save the image
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        with lock:
            stats['downloaded'] += 1
        return True

    except Exception as e:
        with lock:
            stats['errors'] += 1
        return False

def download_worker(queue):
    """Worker function for threaded downloads."""
    while True:
        # Get a task from the queue
        task = queue.get()
        if task is None:
            break
            
        url, save_path = task
        download_image(url, save_path)
        
        # Mark task as done
        queue.task_done()

def process_pose_file(pose_file):
    """Read URLs from a pose file and return a list of (url, save_path) tuples."""
    tasks = []
    pose_name = os.path.basename(pose_file).replace('.txt', '')
    
    try:
        with open(pose_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                rel_path = parts[0].strip()
                url = parts[1].strip()
                
                # Construct the full save path
                save_path = os.path.join(DATASET_DIR, rel_path)
                
                # Skip if file already exists
                if os.path.exists(save_path):
                    with lock:
                        stats['skipped'] += 1
                    continue
                    
                tasks.append((url, save_path))
                with lock:
                    stats['total'] += 1
    
    except Exception as e:
        print(f"Error processing {pose_file}: {e}")
    
    return tasks

def main():
    print(f"Starting download of 20 selected yoga poses from Yoga-82 dataset")
    print(f"Target poses: {[p for p in TARGET_POSES]}")
    
    # Ensure dataset directory exists
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    # Find matching pose files
    pose_files = []
    for pose in TARGET_POSES:
        for f in glob.glob(os.path.join(TXT_FILES_DIR, "*.txt")):
            if pose in os.path.basename(f):
                pose_files.append(f)
                break
    
    # Create download tasks for all poses
    all_tasks = []
    
    print(f"Found {len(pose_files)} pose files to process")
    
    for pose_file in pose_files:
        pose_name = os.path.basename(pose_file).replace('.txt', '')
        print(f"Processing {pose_name}...")
        tasks = process_pose_file(pose_file)
        all_tasks.extend(tasks)
        print(f"  Added {len(tasks)} download tasks for {pose_name}")
    
    print(f"\nPreparing to download {stats['total']} images ({stats['skipped']} already exist)")
    
    # Create download queue and worker threads
    download_queue = Queue()
    threads = []
    
    # Start worker threads
    for i in range(NUM_THREADS):
        t = threading.Thread(target=download_worker, args=(download_queue,))
        t.daemon = True
        t.start()
        threads.append(t)
    
    # Add all tasks to the queue with progress bar
    with tqdm.tqdm(total=len(all_tasks), desc="Downloading images") as pbar:
        last_downloaded = stats['downloaded']
        last_errors = stats['errors']
        
        # Add all tasks to the queue
        for task in all_tasks:
            download_queue.put(task)
        
        # Monitor progress while the queue is being processed
        while not download_queue.empty():
            time.sleep(0.1)
            
            # Update progress bar based on completed downloads and errors
            new_downloaded = stats['downloaded'] - last_downloaded
            new_errors = stats['errors'] - last_errors
            if new_downloaded > 0 or new_errors > 0:
                pbar.update(new_downloaded + new_errors)
                last_downloaded = stats['downloaded']
                last_errors = stats['errors']
    
    # Add None to the queue to signal threads to exit
    for i in range(NUM_THREADS):
        download_queue.put(None)
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    print("\nDownload Summary:")
    print(f"  Successfully downloaded: {stats['downloaded']} images")
    print(f"  Skipped (already existed): {stats['skipped']} images")
    print(f"  Errors: {stats['errors']}")
    print(f"  Total processed: {stats['downloaded'] + stats['skipped'] + stats['errors']}")

if __name__ == "__main__":
    start_time = time.time()
    try:
        main()
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
    finally:
        end_time = time.time()
        print(f"Total execution time: {end_time - start_time:.2f} seconds")