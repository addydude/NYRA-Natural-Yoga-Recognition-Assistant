import os
import shutil
import random
from pathlib import Path

def organize_dataset(source_dir, target_dir, val_split=0.2):
    """
    Organize Yoga-82 dataset into train and validation sets
    
    Args:
        source_dir: Source directory of the Yoga-82 dataset links
        target_dir: Target directory to organize the data
        val_split: Fraction of images for validation
    """
    # Create target directories
    train_dir = os.path.join(target_dir, 'train')
    val_dir = os.path.join(target_dir, 'val')
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)
    
    # Since Yoga-82 has URLs in text files, we'll process differently
    # Get all pose text files
    pose_files = [f for f in os.listdir(source_dir) if f.endswith('.txt')]
    
    # Define the poses we're interested in - 20 selected poses
    target_poses = [
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
    
    # Map from filename to simplified pose name
    pose_name_map = {
        'Child_Pose_or_Balasana_': 'balasana',
        'Tree_Pose_or_Vrksasana_': 'vrksasana',
        'Downward-Facing_Dog_pose_or_Adho_Mukha_Svanasana': 'adho_mukha',
        'Warrior_I_Pose_or_Virabhadrasana_I': 'virabhadrasana_1',
        'Warrior_II_Pose_or_Virabhadrasana_II': 'virabhadrasana_2',
        'Chair_Pose_or_Utkatasana_': 'utkatasana',
        'Cobra_Pose_or_Bhujangasana': 'bhujangasana',
        'Bridge_Pose_or_Setu_Bandh': 'setu_bandha',
        'Boat_Pose_or_Paripurna_Na': 'navasana',
        'Camel_Pose_or_Ustrasana_': 'ustrasana',
        'Cat_Cow_Pose_or_Marjaryas': 'marjaryasana',
        'Bound_Angle_Pose_or_Baddh': 'baddha_konasana',
        'Standing_Forward_Bend_pos': 'uttanasana',
        'Side_Plank_Pose_or_Vasist': 'vasisthasana',
        'Plank_Pose_or_Kumbhakasan': 'kumbhakasana',
        'Seated_Forward_Bend_pose_': 'paschimottanasana',
        'Upward_Bow_(Wheel)_Pose_o': 'urdhva_dhanurasana',
        'Corpse_Pose_or_Savasana_': 'savasana',
        'Dolphin_Pose_or_Ardha_Pin': 'dolphin_pose',
        'Happy_Baby_Pose_or_Ananda': 'ananda_balasana'
    }
    
    print(f"Looking for pose files in: {source_dir}")
    
    # Process each target pose
    for pose_file_name in pose_files:
        pose_name = pose_file_name.replace('.txt', '')
        
        # Check if this is a target pose
        found_target = False
        for target in target_poses:
            if target in pose_name:
                found_target = True
                simplified_name = pose_name_map.get(target, pose_name.lower().replace(' ', '_'))
                break
        
        if not found_target:
            continue
            
        print(f"Processing {pose_name} as {simplified_name}...")
        
        # Create directories for this pose
        os.makedirs(os.path.join(train_dir, simplified_name), exist_ok=True)
        os.makedirs(os.path.join(val_dir, simplified_name), exist_ok=True)
        
        # Read URLs from the pose file
        pose_file_path = os.path.join(source_dir, pose_file_name)
        with open(pose_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            image_urls = [line.strip() for line in f if line.strip()]
        
        print(f"Found {len(image_urls)} image URLs for {simplified_name}")
        
        # NOTE: In a real implementation, you would download these images
        # For now, we'll just create placeholder files to represent the structure
        random.shuffle(image_urls)
        split_idx = int(len(image_urls) * (1 - val_split))
        train_urls = image_urls[:split_idx]
        val_urls = image_urls[split_idx:]
        
        # Create placeholder files
        for i, url in enumerate(train_urls):
            with open(os.path.join(train_dir, simplified_name, f"img_{i}.txt"), 'w') as f:
                f.write(url)
        
        for i, url in enumerate(val_urls):
            with open(os.path.join(val_dir, simplified_name, f"img_{i}.txt"), 'w') as f:
                f.write(url)
        
        print(f"Created {len(train_urls)} train and {len(val_urls)} validation samples for {simplified_name}")

if __name__ == "__main__":
    # Update these paths to match your setup
    SOURCE_DIR = r"D:\NYRAGGbackup - Copy\Yoga-82\yoga_dataset_links"
    TARGET_DIR = r"D:\NYRAGGbackup - Copy\yoga_cnn\dataset"
    
    organize_dataset(SOURCE_DIR, TARGET_DIR)
    print("Dataset organization complete!")