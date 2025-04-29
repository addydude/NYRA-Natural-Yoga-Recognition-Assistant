import os
import shutil
import random
import glob
from pathlib import Path
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import json

# Import scipy explicitly to avoid the NameError
try:
    import scipy
except ImportError:
    print("Warning: scipy not found. Installing scipy...")
    import subprocess
    subprocess.check_call(["pip", "install", "scipy"])
    import scipy

# Base directory configurations
YOGA82_DIR = r"D:\NYRAGGbackup - Copy\Yoga-82"
DATASET_DIR = os.path.join(YOGA82_DIR, "dataset")
OUTPUT_DIR = os.path.join(r"D:\NYRAGGbackup - Copy\yoga_cnn", "processed_dataset")

# Define mapping from pose directory names to simplified class names
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

def create_train_val_split(val_split=0.2, seed=42):
    """
    Organize the downloaded images into training and validation sets.
    
    Args:
        val_split: Fraction of data to use for validation
        seed: Random seed for reproducibility
    
    Returns:
        train_dir, val_dir: Paths to the training and validation directories
    """
    random.seed(seed)
    
    # Create output directories
    train_dir = os.path.join(OUTPUT_DIR, 'train')
    val_dir = os.path.join(OUTPUT_DIR, 'val')
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)
    
    print(f"Organizing dataset into {train_dir} and {val_dir}")
    
    # Find all pose directories in the dataset folder
    pose_dirs = glob.glob(os.path.join(DATASET_DIR, '*'))
    pose_stats = []
    
    for pose_dir in pose_dirs:
        # Skip if not a directory
        if not os.path.isdir(pose_dir):
            continue
            
        # Get the pose name and its simplified class name
        pose_name = os.path.basename(pose_dir)
        class_name = None
        
        # Find the matching simplified name
        for key in pose_name_map:
            if key in pose_name:
                class_name = pose_name_map[key]
                break
        
        if class_name is None:
            print(f"Warning: No class name mapping found for {pose_name}, skipping")
            continue
        
        # Create class directories
        train_class_dir = os.path.join(train_dir, class_name)
        val_class_dir = os.path.join(val_dir, class_name)
        os.makedirs(train_class_dir, exist_ok=True)
        os.makedirs(val_class_dir, exist_ok=True)
        
        # Get all image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            image_files.extend(glob.glob(os.path.join(pose_dir, ext)))
        
        if not image_files:
            print(f"Warning: No images found for {pose_name}, skipping")
            continue
            
        # Shuffle the images
        random.shuffle(image_files)
        
        # Split into train and validation
        split_idx = int(len(image_files) * (1 - val_split))
        train_files = image_files[:split_idx]
        val_files = image_files[split_idx:]
        
        # Copy files
        train_count = 0
        for src in train_files:
            dst = os.path.join(train_class_dir, os.path.basename(src))
            try:
                shutil.copy2(src, dst)
                train_count += 1
            except Exception as e:
                print(f"Error copying {src}: {e}")
        
        val_count = 0
        for src in val_files:
            dst = os.path.join(val_class_dir, os.path.basename(src))
            try:
                shutil.copy2(src, dst)
                val_count += 1
            except Exception as e:
                print(f"Error copying {src}: {e}")
        
        pose_stats.append({
            'pose': pose_name,
            'class_name': class_name,
            'total': len(image_files),
            'train': train_count,
            'val': val_count
        })
        
        print(f"Processed {pose_name} -> {class_name}: {train_count} train, {val_count} validation")
    
    # Print summary
    print("\nDataset Organization Summary:")
    print(f"{'Class Name':<20} | {'Total':<6} | {'Train':<6} | {'Val':<6}")
    print("-" * 50)
    
    total_train = 0
    total_val = 0
    for stat in pose_stats:
        print(f"{stat['class_name']:<20} | {stat['total']:<6} | {stat['train']:<6} | {stat['val']:<6}")
        total_train += stat['train']
        total_val += stat['val']
    
    print("-" * 50)
    print(f"{'Total':<20} | {total_train + total_val:<6} | {total_train:<6} | {total_val:<6}")
    
    return train_dir, val_dir

def create_data_generators(train_dir, val_dir, img_size=(224, 224), batch_size=32):
    """
    Create image data generators for training and validation.
    
    Args:
        train_dir: Path to training directory
        val_dir: Path to validation directory
        img_size: Image size for model input
        batch_size: Batch size for training
        
    Returns:
        train_generator, val_generator: Data generators for training and validation
    """
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # Only rescaling for validation
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    # Create generators
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical'
    )
    
    val_generator = val_datagen.flow_from_directory(
        val_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical'
    )
    
    return train_generator, val_generator

def visualize_samples(generator, class_indices, num_samples=5):
    """
    Visualize samples from a data generator.
    
    Args:
        generator: Image data generator
        class_indices: Dictionary mapping class indices to class names
        num_samples: Number of samples to visualize
    """
    # Modified approach to avoid issues with the generator's transform functions
    try:
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.join(OUTPUT_DIR, 'sample_images')), exist_ok=True)
        
        # Get class directory paths
        class_dirs = {}
        for class_name, class_idx in class_indices.items():
            class_dir = os.path.join(OUTPUT_DIR, 'train', class_name)
            if os.path.exists(class_dir):
                class_dirs[class_name] = class_dir
        
        # Select random images from each class
        plt.figure(figsize=(15, num_samples * 3))
        
        # Reverse the class indices mapping
        label_map = {v: k for k, v in class_indices.items()}
        
        # Counter for subplot positions
        count = 0
        
        # Get a few random samples from different classes
        for class_name, class_dir in list(class_dirs.items())[:num_samples]:
            image_files = glob.glob(os.path.join(class_dir, '*.jpg'))
            if not image_files:
                image_files = glob.glob(os.path.join(class_dir, '*.jpeg'))
            if not image_files:
                image_files = glob.glob(os.path.join(class_dir, '*.png'))
            
            if image_files:
                # Select a random image
                image_path = random.choice(image_files)
                
                # Load and display the image
                count += 1
                img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224, 224))
                plt.subplot(num_samples, 1, count)
                plt.imshow(img)
                plt.title(f"Class: {class_name}")
                plt.axis('off')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'sample_images.png'))
        print(f"Sample images saved to {os.path.join(OUTPUT_DIR, 'sample_images.png')}")
        
    except Exception as e:
        print(f"Error visualizing samples: {e}")
        print("Continuing with training despite visualization error.")

if __name__ == "__main__":
    # Create train/val split
    train_dir, val_dir = create_train_val_split()
    
    # Create data generators
    train_generator, val_generator = create_data_generators(train_dir, val_dir)
    
    # Visualize some samples
    visualize_samples(train_generator, train_generator.class_indices, num_samples=5)
    
    print("\nDataset is ready for training!")

def load_yoga_dataset(data_dir, img_size=(224, 224), batch_size=32):
    """
    Load and preprocess yoga pose images
    
    Args:
        data_dir: Directory containing train and val folders with class subfolders
        img_size: Input size for the model
        batch_size: Batch size for training
        
    Returns:
        train_ds, val_ds, class_indices: Training and validation datasets, class mapping
    """
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # Only rescale for validation
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    # Check if directories exist
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'val')
    
    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        raise FileNotFoundError(f"Train or validation directory not found in {data_dir}")
    
    # Load images from directories
    train_ds = train_datagen.flow_from_directory(
        train_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=True
    )
    
    val_ds = val_datagen.flow_from_directory(
        val_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False
    )
    
    return train_ds, val_ds, train_ds.class_indices

def save_class_indices(class_indices, file_path):
    """Save the class indices to a JSON file"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Convert class indices to a format suitable for inference
    class_mapping = {str(v): k for k, v in class_indices.items()}
    
    with open(file_path, 'w') as f:
        json.dump(class_mapping, f, indent=4)
    
    print(f"Class indices saved to {file_path}")

def load_class_indices(file_path):
    """Load the class indices from a JSON file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Class indices file not found at {file_path}")
    
    with open(file_path, 'r') as f:
        class_mapping = json.load(f)
    
    return class_mapping

def check_dataset_stats(data_dir):
    """Check statistics of the dataset"""
    stats = {"train": {}, "val": {}}
    
    for split in ["train", "val"]:
        split_dir = os.path.join(data_dir, split)
        if not os.path.exists(split_dir):
            print(f"{split_dir} does not exist!")
            continue
        
        total_images = 0
        for class_name in os.listdir(split_dir):
            class_dir = os.path.join(split_dir, class_name)
            if not os.path.isdir(class_dir):
                continue
            
            image_count = len([f for f in os.listdir(class_dir) 
                              if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
            stats[split][class_name] = image_count
            total_images += image_count
        
        stats[split]["total"] = total_images
    
    return stats