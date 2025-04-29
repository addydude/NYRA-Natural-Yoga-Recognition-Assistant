import os
import numpy as np
import tensorflow as tf
import cv2
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Set memory growth for GPU to avoid OOM errors
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

# Configuration
IMG_SIZE = 224
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'efficientnet')
MODEL_PATH = os.path.join(MODEL_DIR, 'yoga_efficientnet_best.h5')
PREDICTIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'predictions')
os.makedirs(PREDICTIONS_DIR, exist_ok=True)

# Class labels for yoga poses
YOGA_CLASSES = [
    'adho_mukha_svanasana', 'ardha_chandrasana', 'balasana',
    'dhanurasana', 'padmasana', 'parsvakonasana', 'phalakasana',
    'setu_bandha_sarvangasana', 'tadasana', 'trikonasana',
    'urdhva_mukha_svanasana', 'ustrasana', 'uttanasana',
    'virabhadrasana_i', 'virabhadrasana_ii', 'vriksasana',
    'halasana', 'matsyasana', 'paschimottanasana', 'bhujangasana'
]

def preprocess_image(img_path):
    """Preprocess image for prediction"""
    # Load image
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Resize to expected size
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    
    # Normalize pixel values
    img = img / 255.0
    
    # Expand dimensions to create batch
    return np.expand_dims(img, axis=0)

def predict_pose(img_path, model):
    """Predict yoga pose from an image"""
    # Preprocess image
    preprocessed_img = preprocess_image(img_path)
    
    # Make prediction
    predictions = model.predict(preprocessed_img)
    
    # Get class with highest probability
    predicted_class_idx = np.argmax(predictions[0])
    predicted_class = YOGA_CLASSES[predicted_class_idx]
    confidence = predictions[0][predicted_class_idx]
    
    # Get top 3 predictions
    top_indices = np.argsort(predictions[0])[-3:][::-1]
    top_classes = [(YOGA_CLASSES[i], predictions[0][i]) for i in top_indices]
    
    return predicted_class, confidence, top_classes

def visualize_prediction(img_path, predicted_class, confidence, top_classes, output_path=None):
    """Visualize prediction results"""
    # Load and display image
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    plt.figure(figsize=(10, 8))
    
    # Display image
    plt.subplot(1, 2, 1)
    plt.imshow(img)
    plt.title(f"Predicted: {predicted_class.replace('_', ' ')}\nConfidence: {confidence:.2%}")
    plt.axis('off')
    
    # Display top 3 predictions as bar chart
    plt.subplot(1, 2, 2)
    labels = [cls.replace('_', ' ') for cls, _ in top_classes]
    scores = [score for _, score in top_classes]
    
    y_pos = np.arange(len(labels))
    plt.barh(y_pos, scores, align='center', alpha=0.7)
    plt.yticks(y_pos, labels)
    plt.xlabel('Confidence')
    plt.title('Top 3 Predictions')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path)
        print(f"Prediction visualization saved to {output_path}")
    else:
        plt.show()
    
    plt.close()

def main():
    # Check if model file exists
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found at {MODEL_PATH}")
        print("Please train the model first using train_efficientnet.py")
        return
    
    # Load model
    print(f"Loading model from {MODEL_PATH}...")
    model = load_model(MODEL_PATH)
    print("Model loaded successfully!")
    
    # Get input images from user
    while True:
        img_path = input("\nEnter path to yoga pose image (or 'q' to quit): ")
        
        if img_path.lower() == 'q':
            break
        
        if not os.path.exists(img_path):
            print(f"Error: Image file not found at {img_path}")
            continue
        
        # Predict pose
        try:
            predicted_class, confidence, top_classes = predict_pose(img_path, model)
            
            # Print results
            print(f"\nPredicted pose: {predicted_class.replace('_', ' ')}")
            print(f"Confidence: {confidence:.2%}")
            print("\nTop 3 predictions:")
            for i, (cls, score) in enumerate(top_classes, 1):
                print(f"{i}. {cls.replace('_', ' ')} - {score:.2%}")
            
            # Save visualization
            base_name = os.path.basename(img_path).split('.')[0]
            output_path = os.path.join(PREDICTIONS_DIR, f"{base_name}_efficientnet_prediction.png")
            visualize_prediction(img_path, predicted_class, confidence, top_classes, output_path)
            
        except Exception as e:
            print(f"Error during prediction: {str(e)}")

if __name__ == "__main__":
    main()