import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import tensorflow as tf

# Configure paths
MODEL_DIR = os.path.join(r"D:\NYRAGGbackup - Copy\yoga_cnn", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "yoga_model_final.h5")
CLASS_INDICES_PATH = os.path.join(MODEL_DIR, "class_indices.json")
STATIC_IMAGES_DIR = os.path.join(r"D:\NYRAGGbackup - Copy", "static", "images")
OUTPUT_DIR = os.path.join(r"D:\NYRAGGbackup - Copy\yoga_cnn", "predictions")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_class_indices(file_path):
    """Load the class indices from the JSON file"""
    try:
        with open(file_path, 'r') as f:
            class_indices = json.load(f)
        # The file contains a mapping from class name -> index
        # We want to return a mapping from index -> class name
        return {int(k): v for k, v in class_indices.items()}
    except FileNotFoundError:
        print(f"Error: Class indices file not found at {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON file at {file_path}")
        sys.exit(1)

def load_and_preprocess_image(img_path, target_size=(224, 224)):
    """Load and preprocess an image for prediction"""
    try:
        img = image.load_img(img_path, target_size=target_size)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        # Normalize the image
        img_array = img_array / 255.0
        return img_array, img
    except Exception as e:
        print(f"Error loading image {img_path}: {str(e)}")
        return None, None

def predict_pose(model, img_path, class_names):
    """Predict the yoga pose in an image"""
    # Load and preprocess image
    img_array, img = load_and_preprocess_image(img_path)
    if img_array is None:
        return None
    
    # Make prediction
    predictions = model.predict(img_array, verbose=0)
    predicted_class = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_class])
    
    # Get top 3 predictions
    top_indices = predictions[0].argsort()[-3:][::-1]
    top_predictions = []
    
    for idx in top_indices:
        class_name = None
        for name, class_idx in class_names.items():
            if class_idx == idx:
                class_name = name
                break
        if class_name:
            top_predictions.append((class_name, float(predictions[0][idx])))
    
    # Get class name for the predicted class
    predicted_class_name = None
    for name, class_idx in class_names.items():
        if class_idx == predicted_class:
            predicted_class_name = name
            break
    
    return {
        'class_name': predicted_class_name,
        'confidence': confidence,
        'top_3': top_predictions,
        'image': img
    }

def visualize_prediction(result, img_path):
    """Visualize the prediction result"""
    if result is None:
        print(f"Couldn't process {img_path}")
        return
    
    # Create figure
    plt.figure(figsize=(10, 8))
    
    # Display image
    plt.imshow(result['image'])
    
    # Add title with prediction
    plt.title(f"Predicted: {result['class_name']}\nConfidence: {result['confidence']:.2f}", fontsize=14)
    
    # Add top 3 predictions as text
    prediction_text = "Top 3 predictions:\n"
    for i, (pose, conf) in enumerate(result['top_3']):
        prediction_text += f"{i+1}. {pose}: {conf:.3f}\n"
    
    plt.figtext(0.5, 0.01, prediction_text, ha="center", fontsize=12, 
                bbox={"facecolor":"orange", "alpha":0.5, "pad":5})
    
    plt.axis('off')
    
    # Save the visualization
    base_name = os.path.basename(img_path)
    save_path = os.path.join(OUTPUT_DIR, f"prediction_{os.path.splitext(base_name)[0]}.png")
    plt.savefig(save_path, bbox_inches='tight')
    print(f"Prediction visualization saved to {save_path}")
    plt.close()

def main():
    # Load the model
    print("Loading model...")
    try:
        model = load_model(MODEL_PATH)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        sys.exit(1)
    
    # Load class indices
    print("Loading class indices...")
    try:
        with open(CLASS_INDICES_PATH, 'r') as f:
            class_indices = json.load(f)
        
        # In the file, the format is {class_name: index}
        # Invert the mapping for our prediction function
        class_names = {}
        for name, idx in class_indices.items():
            class_names[name] = idx
            
        print(f"Found {len(class_names)} classes")
        print("Class mapping:")
        for name, idx in sorted(class_names.items(), key=lambda x: x[1]):
            print(f"  {idx}: {name}")
    except Exception as e:
        print(f"Error loading class indices: {str(e)}")
        sys.exit(1)
    
    # Get list of sample images to test
    test_images = []
    
    # Look in the static images directory for yoga poses
    if os.path.exists(STATIC_IMAGES_DIR):
        for filename in os.listdir(STATIC_IMAGES_DIR):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')) and any(pose in filename.lower() for pose in [
                'adho_mukha', 'balasana', 'vrksana', 'virabhadrasana', 'tadasan', 'trikonasana'
            ]):
                test_images.append(os.path.join(STATIC_IMAGES_DIR, filename))
    
    # If we couldn't find any images, look in the processed dataset validation folder
    if not test_images:
        val_dir = os.path.join(r"D:\NYRAGGbackup - Copy\yoga_cnn", "processed_dataset", "val")
        if os.path.exists(val_dir):
            for class_dir in os.listdir(val_dir):
                class_path = os.path.join(val_dir, class_dir)
                if os.path.isdir(class_path):
                    # Pick one random image from each class
                    image_files = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    if image_files:
                        test_images.append(os.path.join(class_path, np.random.choice(image_files)))
                        # Limit to 5 test images
                        if len(test_images) >= 5:
                            break
    
    if not test_images:
        print("No test images found. Please specify image paths as arguments.")
        # Still continue with user-provided images if any
        if len(sys.argv) > 1:
            test_images = sys.argv[1:]
    
    # If still no images, exit
    if not test_images:
        print("No images to process. Exiting.")
        sys.exit(0)
    
    # Process each image
    for img_path in test_images:
        if os.path.exists(img_path):
            print(f"Processing {img_path}...")
            result = predict_pose(model, img_path, class_names)
            visualize_prediction(result, img_path)
        else:
            print(f"Image not found: {img_path}")
    
    print("\nPrediction completed!")
    print(f"Results saved in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()