import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
import json
import os
import time
import PoseModule as pm

class CNNPoseClassifier:
    def __init__(self, model_path=None, class_indices_path=None):
        """
        Initialize the CNN-based yoga pose classifier
        
        Args:
            model_path: Path to the trained model
            class_indices_path: Path to the class indices JSON file
        """
        self.model_path = model_path or r"D:\NYRAGGbackup - Copy\yoga_cnn\saved_model\yoga_pose_model"
        self.class_indices_path = class_indices_path or r"D:\NYRAGGbackup - Copy\yoga_cnn\saved_model\class_indices.json"
        
        # Flag to track if model is loaded
        self.model_loaded = False
        
        try:
            # Load the model and class indices
            self._load_model()
            self._load_class_indices()
            self.model_loaded = True
        except FileNotFoundError as e:
            print(f"Warning: {str(e)}")
            print("CNN model not found. Using angle-based detection instead.")
            self.model_loaded = False
        
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
            
        print(f"Loading CNN model from {self.model_path}")
        self.model = tf.keras.models.load_model(self.model_path)
    
    def _load_class_indices(self):
        """Load class indices mapping"""
        if not os.path.exists(self.class_indices_path):
            raise FileNotFoundError(f"Class indices not found at {self.class_indices_path}")
            
        with open(self.class_indices_path, 'r') as f:
            self.class_mapping = json.load(f)
        
        # Convert string indices to integers
        self.class_mapping = {int(k): v for k, v in self.class_mapping.items()}
        
        # Create reverse mapping from pose name to standard id
        self.pose_name_to_id = {
            'vrksana': 'vrksana',
            'tadasana': 'tadasan',
            'balasana': 'balasana',
            'trikonasana': 'trikonasana',
            'virabhadrasana': 'virabhadrasana',
            'adho_mukha': 'adhomukha'
        }
    
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
    
    def classify_pose(self, img):
        """
        Classify yoga pose using the trained CNN model
        
        Args:
            img: OpenCV image in BGR format
            
        Returns:
            pose_id: Standard pose ID used in the application
            confidence: Confidence score
            pose_name: The raw pose name from the classifier
        """
        if not self.model_loaded:
            return None, 0.0, "CNN model not loaded"
            
        # Detect pose landmarks
        results = self.pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            return None, 0.0, "No person detected"
            
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
        
        # Convert to standard pose ID used in the application
        pose_id = self.pose_name_to_id.get(pose_name, None)
        
        return pose_id, confidence, pose_name


class HybridPoseDetector:
    """
    A hybrid approach that combines CNN-based classification with angle-based verification
    """
    def __init__(self, pose_name="vrksana", use_cnn=True):
        self.pose_name = pose_name
        self.use_cnn = use_cnn
        
        # Initialize the angle-based detector
        self.angle_detector = pm.PoseDetector(pose_name=pose_name)
        
        # Initialize the CNN-based detector if requested
        self.cnn_detector = CNNPoseClassifier() if use_cnn else None
        self.cnn_available = self.cnn_detector is not None and self.cnn_detector.model_loaded
        
        # Confidence threshold for CNN detection
        self.confidence_threshold = 0.7
        
        # Store the last CNN prediction and timestamp
        self.last_prediction = None
        self.last_prediction_time = 0
        self.prediction_refresh_time = 1.0  # Refresh prediction every second
        
    def findPose(self, frame, draw=True):
        """Find pose using the angle-based detector"""
        return self.angle_detector.findPose(frame, draw)
        
    def getPosition(self, frame, draw=True):
        """Get position using the angle-based detector"""
        return self.angle_detector.getPosition(frame, draw)
        
    def findAngle(self, img, p1, p2, p3, draw=True):
        """Find angle using the angle-based detector"""
        return self.angle_detector.findAngle(img, p1, p2, p3, draw)
        
    def showBreathingGuide(self, frame):
        """Show breathing guide using the angle-based detector"""
        return self.angle_detector.showBreathingGuide(frame)
        
    def get_pose_confidence(self, frame):
        """
        Get pose confidence using CNN if available
        
        Returns:
            pose_id: The detected pose ID or None
            confidence: Confidence score (0-1)
            is_cnn: Whether CNN was used for detection
        """
        # If CNN not available, we can't provide confidence directly
        if not self.cnn_available:
            return None, 0.0, False
            
        current_time = time.time()
        
        # Only refresh prediction periodically to save processing power
        if (current_time - self.last_prediction_time) >= self.prediction_refresh_time or self.last_prediction is None:
            pose_id, confidence, pose_name = self.cnn_detector.classify_pose(frame)
            self.last_prediction = (pose_id, confidence, pose_name)
            self.last_prediction_time = current_time
        else:
            pose_id, confidence, pose_name = self.last_prediction
            
        return pose_id, confidence, True