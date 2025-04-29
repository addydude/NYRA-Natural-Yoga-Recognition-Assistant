import cv2
import numpy as np
import tensorflow as tf
import json
import os
import mediapipe as mp

class PoseClassifier:
    def __init__(self, model_path=None, class_indices_path=None):
        """
        Initialize the yoga pose classifier
        
        Args:
            model_path: Path to the trained model
            class_indices_path: Path to the class indices JSON file
        """
        self.model_path = model_path or r"D:\NYRAGGbackup - Copy\yoga_cnn\saved_model\yoga_pose_model"
        self.class_indices_path = class_indices_path or r"D:\NYRAGGbackup - Copy\yoga_cnn\saved_model\class_indices.json"
        
        # Load the model
        self._load_model()
        
        # Load class indices mapping
        self._load_class_indices()
        
        # Initialize MediaPipe Pose for detecting person
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.5
        )
        
        # For drawing landmarks
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
    
    def _load_model(self):
        """Load the trained model"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
            
        print(f"Loading model from {self.model_path}")
        self.model = tf.keras.models.load_model(self.model_path)
    
    def _load_class_indices(self):
        """Load class indices mapping"""
        if not os.path.exists(self.class_indices_path):
            raise FileNotFoundError(f"Class indices not found at {self.class_indices_path}")
            
        with open(self.class_indices_path, 'r') as f:
            self.class_mapping = json.load(f)
        
        # Convert string indices to integers
        self.class_mapping = {int(k): v for k, v in self.class_mapping.items()}
    
    def _preprocess_image(self, img):
        """
        Preprocess image for the CNN model
        
        Args:
            img: OpenCV image in BGR format
            
        Returns:
            Preprocessed image tensor
        """
        # Resize to the expected input size
        img_resized = cv2.resize(img, (224, 224))
        # Convert BGR to RGB (TensorFlow models expect RGB)
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        # Normalize pixel values
        img_normalized = img_rgb / 255.0
        # Add batch dimension
        img_batch = np.expand_dims(img_normalized, axis=0)
        return img_batch
    
    def _crop_person(self, img, results):
        """
        Crop the image to focus on the person
        
        Args:
            img: OpenCV image
            results: MediaPipe pose detection results
            
        Returns:
            Cropped image around the person
        """
        if not results.pose_landmarks:
            return img
            
        h, w, _ = img.shape
        
        # Get bounding box from landmarks
        landmarks = [[lmk.x * w, lmk.y * h] for lmk in results.pose_landmarks.landmark]
        landmarks = np.array(landmarks)
        
        # Get the min/max coordinates
        x_min, y_min = np.min(landmarks, axis=0)
        x_max, y_max = np.max(landmarks, axis=0)
        
        # Add padding
        padding = 30
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        x_max = min(w, x_max + padding)
        y_max = min(h, y_max + padding)
        
        # Crop the image
        cropped_img = img[int(y_min):int(y_max), int(x_min):int(x_max)]
        
        # If cropping failed, return original
        if cropped_img.size == 0:
            return img
            
        return cropped_img
    
    def classify_pose(self, img, draw=False):
        """
        Classify yoga pose using the trained CNN model
        
        Args:
            img: OpenCV image in BGR format
            draw: Whether to draw pose landmarks on the image
            
        Returns:
            pose_name: Detected pose name
            confidence: Confidence score
            processed_img: Image with landmarks drawn if draw=True
        """
        # Make a copy of the image
        processed_img = img.copy()
        
        # Detect pose landmarks
        results = self.pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            return "No person detected", 0.0, processed_img
            
        # Draw pose landmarks if requested
        if draw:
            self.mp_drawing.draw_landmarks(
                processed_img,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
        # Crop the image to focus on the person
        cropped_img = self._crop_person(img, results)
        
        # Preprocess the cropped image
        processed_tensor = self._preprocess_image(cropped_img)
        
        # Run inference
        predictions = self.model.predict(processed_tensor, verbose=0)[0]
        
        # Get the predicted class and confidence
        predicted_class_idx = np.argmax(predictions)
        confidence = float(predictions[predicted_class_idx])
        
        # Get the class name
        pose_name = self.class_mapping.get(predicted_class_idx, "Unknown")
        
        return pose_name, confidence, processed_img