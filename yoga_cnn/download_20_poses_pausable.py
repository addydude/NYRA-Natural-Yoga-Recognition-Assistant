import os
import requests
import time
import glob
from pathlib import Path
import tqdm
import threading
from queue import Queue
import json
import signal
import sys

# --- Configuration ---
# Base directories
YOGA82_DIR = r"D:\NYRAGGbackup - Copy\Yoga-82"
DATASET_DIR = os.path.join(YOGA82_DIR, "dataset")
TXT_FILES_DIR = os.path.join(YOGA82_DIR, "yoga_dataset_links")

# Request settings
REQUEST_TIMEOUT = 15
NUM_THREADS = 5

# State file for resuming downloads
STATE_FILE = os.path.join(YOGA82_DIR, "download_state.json")
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

# Global counters for statistics
stats = {
    'downloaded': 0,
    'skipped': 0,
    'errors': 0,
    'total': 0
}

# Global flags for controlling execution
PAUSE_FLAG = False
STOP_FLAG = False

# Lock for thread-safe operations
lock = threading.Lock()

def load_state():
    """Load the previous download state if it exists."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading state file: {e}")
    return {
        "completed_poses": [],
        "downloaded_files": [],
        "stats": {
            "downloaded": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0
        }
    }

def save_state(completed_poses, downloaded_files, current_stats):
    """Save the current download state to a file."""
    state = {
        "completed_poses": completed_poses,
        "downloaded_files": downloaded_files,
        "stats": current_stats
    }
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
        print(f"Download state saved to {STATE_FILE}")
    except Exception as e:
        print(f"Error saving state file: {e}")

def download_image(url, save_path, downloaded_files):
    """Downloads an image from a URL and saves it to the specified path."""
    try:
        # Create the directory if it doesn't exist
        directory = os.path.dirname(save_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # Check if file already exists or was previously downloaded
        if os.path.exists(save_path) or save_path in downloaded_files:
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
                if PAUSE_FLAG or STOP_FLAG:
                    # Stop downloading if paused or stopped
                    return False
                f.write(chunk)
                
        with lock:
            stats['downloaded'] += 1
            downloaded_files.append(save_path)
        return True

    except Exception as e:
        with lock:
            stats['errors'] += 1
        return False

def download_worker(queue, downloaded_files):
    """Worker function for threaded downloads."""
    while not STOP_FLAG:
        try:
            # Get a task from the queue with a timeout
            task = queue.get(timeout=1)
            if task is None:
                break
                
            url, save_path = task
            
            # Skip if paused
            if PAUSE_FLAG:
                # Put the task back in the queue and exit
                queue.put(task)
                break
                
            download_image(url, save_path, downloaded_files)
            
            # Mark task as done
            queue.task_done()
        except Exception:
            # Queue is empty or timeout
            if PAUSE_FLAG or STOP_FLAG:
                break

def process_pose_file(pose_file, downloaded_files):
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
                
                # Skip if file already exists or was previously downloaded
                if os.path.exists(save_path) or save_path in downloaded_files:
                    with lock:
                        stats['skipped'] += 1
                    continue
                    
                tasks.append((url, save_path))
                with lock:
                    stats['total'] += 1
    
    except Exception as e:
        print(f"Error processing {pose_file}: {e}")
    
    return tasks

def signal_handler(sig, frame):
    """Handle keyboard interrupt to pause or stop the download."""
    global PAUSE_FLAG, STOP_FLAG
    
    if PAUSE_FLAG:  # If already paused, stop completely
        print("\nStopping download. Progress has been saved.")
        STOP_FLAG = True
    else:  # First interrupt, pause the download
        print("\nPausing download. Press Ctrl+C again to stop completely, or run the script again later to resume.")
        PAUSE_FLAG = True

def main():
    global stats
    
    # Register signal handler for graceful pause/termination
    signal.signal(signal.SIGINT, signal_handler)
    
    # Load previous state if it exists
    state = load_state()
    completed_poses = state["completed_poses"]
    downloaded_files = state["downloaded_files"]
    
    # Update stats from previous run
    if state["stats"]:
        stats = state["stats"]
    
    print(f"Starting download of 20 selected yoga poses from Yoga-82 dataset")
    print(f"Target poses: {len(TARGET_POSES)} poses")
    
    if completed_poses:
        print(f"Resuming from previous run. Already completed: {len(completed_poses)} poses.")
    
    # Ensure dataset directory exists
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    # Find matching pose files
    pose_files = []
    for pose in TARGET_POSES:
        # Skip if already completed
        if pose in completed_poses:
            continue
            
        for f in glob.glob(os.path.join(TXT_FILES_DIR, "*.txt")):
            if pose in os.path.basename(f):
                pose_files.append(f)
                break
    
    if not pose_files:
        print("All target poses already downloaded or no matching pose files found.")
        return
    
    # Create download tasks for all poses
    all_tasks = []
    
    print(f"Found {len(pose_files)} pose files to process")
    
    for pose_file in pose_files:
        pose_name = os.path.basename(pose_file).replace('.txt', '')
        print(f"Processing {pose_name}...")
        tasks = process_pose_file(pose_file, downloaded_files)
        all_tasks.extend(tasks)
        print(f"  Added {len(tasks)} download tasks for {pose_name}")
    
    if not all_tasks:
        print("No new images to download.")
        return
        
    print(f"\nPreparing to download {stats['total']} images ({stats['skipped']} already exist)")
    
    # Create download queue and worker threads
    download_queue = Queue()
    threads = []
    
    # Start worker threads
    for i in range(NUM_THREADS):
        t = threading.Thread(target=download_worker, args=(download_queue, downloaded_files))
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
            if PAUSE_FLAG or STOP_FLAG:
                break
                
            time.sleep(0.1)
            
            # Update progress bar based on completed downloads and errors
            new_downloaded = stats['downloaded'] - last_downloaded
            new_errors = stats['errors'] - last_errors
            if new_downloaded > 0 or new_errors > 0:
                pbar.update(new_downloaded + new_errors)
                last_downloaded = stats['downloaded']
                last_errors = stats['errors']
                
                # Save state periodically (every 50 downloads)
                if stats['downloaded'] % 50 == 0:
                    current_pose = os.path.basename(pose_files[0]).replace('.txt', '')
                    save_state(completed_poses, downloaded_files, stats)
    
    # If paused or stopped, save the current state
    if PAUSE_FLAG or STOP_FLAG:
        save_state(completed_poses, downloaded_files, stats)
        return
    
    # Add None to the queue to signal threads to exit
    for i in range(NUM_THREADS):
        download_queue.put(None)
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    # Mark all processed poses as completed
    for pose_file in pose_files:
        pose = os.path.basename(pose_file).replace('.txt', '')
        if pose not in completed_poses:
            completed_poses.append(pose)
    
    # Save the final state
    save_state(completed_poses, downloaded_files, stats)
    
    print("\nDownload Summary:")
    print(f"  Successfully downloaded: {stats['downloaded']} images")
    print(f"  Skipped (already existed): {stats['skipped']} images")
    print(f"  Errors: {stats['errors']}")
    print(f"  Total processed: {stats['downloaded'] + stats['skipped'] + stats['errors']}")

if __name__ == "__main__":
    start_time = time.time()
    try:
        main()
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        # Save state on unexpected error
        save_state([], [], stats)
    finally:
        end_time = time.time()
        print(f"Total execution time: {end_time - start_time:.2f} seconds")