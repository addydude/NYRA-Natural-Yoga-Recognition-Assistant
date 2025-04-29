import os
import glob
from pathlib import Path

# Base directory configurations
YOGA82_DIR = r"D:\NYRAGGbackup - Copy\Yoga-82"
DATASET_DIR = os.path.join(YOGA82_DIR, "dataset")

# List of target poses we wanted to download
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

def check_downloads():
    print("Checking downloaded images status...")
    print("-" * 60)
    print(f"{'Pose Name':<35} | {'Downloaded':<10} | {'Status':<10}")
    print("-" * 60)
    
    total_downloaded = 0
    total_expected = 0
    missing_poses = []
    
    # Load the pose directories
    for pose in TARGET_POSES:
        pose_dir_pattern = os.path.join(DATASET_DIR, pose + '*')
        pose_dirs = glob.glob(pose_dir_pattern)
        
        if pose_dirs:
            pose_dir = pose_dirs[0]  # Take the first matching directory
            pose_name = os.path.basename(pose_dir)
            
            # Count image files in this pose directory
            image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png']:
                image_files.extend(glob.glob(os.path.join(pose_dir, ext)))
            
            count = len(image_files)
            total_downloaded += count
            
            # Get expected count from the text file
            txt_file = os.path.join(YOGA82_DIR, "yoga_dataset_links", pose_name + ".txt")
            expected = 0
            if os.path.exists(txt_file):
                with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                    expected = len([line for line in f.readlines() if line.strip()])
            
            total_expected += expected
            
            status = "✅ Good"
            if count == 0:
                status = "❌ Missing"
                missing_poses.append(pose_name)
            elif count < expected * 0.5:  # Less than 50% downloaded
                status = "⚠️ Partial"
            
            print(f"{pose_name[:35]:<35} | {count:<10} | {status:<10} ({count}/{expected})")
        else:
            print(f"{pose:<35} | {0:<10} | ❌ Missing (0/0)")
            missing_poses.append(pose)
    
    print("-" * 60)
    print(f"Total downloaded images: {total_downloaded} of {total_expected}")
    print(f"Download completion: {total_downloaded/total_expected*100:.2f}% of expected images")
    
    if missing_poses:
        print("\nPoses with no images:")
        for pose in missing_poses:
            print(f"- {pose}")
    else:
        print("\nAll poses have some images downloaded!")
    
    return total_downloaded, missing_poses

if __name__ == "__main__":
    check_downloads()