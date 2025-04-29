import cv2
import numpy as np
import time
import os
import PoseModule as pm
from HuggingFacePoseClassifier import HuggingFacePoseClassifier

class HuggingFaceHybridDetector:
    """
    A hybrid approach that combines Hugging Face transformer-based classification with angle-based verification
    """
    def __init__(self, pose_name="vrksana", use_hf=True):
        self.pose_name = pose_name
        self.use_hf = use_hf
        
        # Initialize the angle-based detector
        self.angle_detector = pm.PoseDetector(pose_name=pose_name)
        
        # Initialize the Hugging Face-based detector if requested
        self.hf_detector = HuggingFacePoseClassifier() if use_hf else None
        self.hf_available = self.hf_detector is not None
        
        # Confidence threshold for HF detection
        self.confidence_threshold = 0.7
        
        # Store the last HF prediction and timestamp
        self.last_prediction = None
        self.last_prediction_time = 0
        self.prediction_refresh_time = 1.0  # Refresh prediction every second
        
        # Performance optimization variables
        self.frame_count = 0
        self.process_every_n_frames = 3  # Only process every 3rd frame for HF model
        self.last_frame_time = time.time()
        self.target_fps = 15  # Target 15 FPS
        self.frame_duration = 1.0 / self.target_fps
        
        print(f"Initializing HuggingFaceHybridDetector with pose: {pose_name}")
        
        # No need for manual mappings as we now have them in the HuggingFacePoseClassifier class
        
    def findPose(self, frame, draw=True):
        """Find pose using the angle-based detector"""
        # Limit frame rate for smoother experience
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        
        # If processing too fast, add a small delay to maintain target FPS
        if elapsed < self.frame_duration:
            delay_time = self.frame_duration - elapsed
            time.sleep(delay_time)
            
        self.last_frame_time = time.time()
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
        Get pose confidence using Hugging Face model if available
        
        Returns:
            pose_id: The detected pose ID or None
            confidence: Confidence score (0-1)
            is_hf: Whether Hugging Face model was used for detection
        """
        # If Hugging Face model not available, we can't provide confidence directly
        if not self.hf_available:
            return None, 0.0, False
            
        current_time = time.time()
        
        # Only refresh prediction periodically to save processing power
        if (current_time - self.last_prediction_time) >= self.prediction_refresh_time or self.last_prediction is None:
            # Skip frames to improve performance
            self.frame_count += 1
            
            # Only process every few frames to reduce CPU load
            if self.frame_count % self.process_every_n_frames == 0:
                # Down-sample the frame for faster processing
                small_frame = cv2.resize(frame, (224, 224))
                
                # Directly use the classifier's built-in image handling
                pose_name, confidence = self.hf_detector.classify_image(small_frame)
                
                # Store the result including the pose name that matches our application
                self.last_prediction = (pose_name, confidence, pose_name)
                self.last_prediction_time = current_time
                
                # Log for debugging
                print(f"Detected pose: {pose_name} with confidence: {confidence:.2f}")
            else:
                # Use previous prediction to save resources
                pose_id, confidence, pose_name = self.last_prediction if self.last_prediction else (None, 0.0, None)
        else:
            pose_id, confidence, pose_name = self.last_prediction if self.last_prediction else (None, 0.0, None)
            
        return pose_name, confidence, True
    
    def classify_pose(self, img):
        """
        Classify the yoga pose using Hugging Face model
        """
        if not self.use_hf or self.hf_detector is None:
            return None, 0.0
        
        # Skip frames for better performance
        self.frame_count += 1
        if self.frame_count % self.process_every_n_frames != 0 and self.last_prediction is not None:
            # Return previous prediction for skipped frames
            pose_id, confidence, pose_name = self.last_prediction
            return pose_name, confidence
        
        # Downsample image for faster processing
        resized_img = cv2.resize(img, (224, 224)) 
        
        # Use the Hugging Face classifier to predict the pose
        # This now returns the pose name already mapped to our application's naming convention
        pose_name, confidence = self.hf_detector.classify_image(resized_img)
        
        # Save prediction for future frame skipping
        self.last_prediction = (pose_name, confidence, pose_name)
        
        # Debug log
        print(f"Classified as {pose_name} with {confidence*100:.1f}% confidence (Expected pose: {self.pose_name})")
        
        return pose_name, confidence
    
    def detect_hybrid(self, img, draw=True):
        """
        Detect pose using both angle-based and HuggingFace-based methods
        Returns:
            - is_correct: Boolean indicating if pose is correct
            - angle_result: Result from angle-based detection
            - hf_result: Result from HuggingFace-based detection (pose name and confidence)
            - img: Processed image with annotations if draw=True
        """
        # Find pose using angle-based detector
        img = self.findPose(img, draw)
        lmList = self.getPosition(img, draw)
        
        # Get angle-based detection result
        angle_result = False
        if len(lmList) > 0:
            angle_result = self.angle_detector.detect_pose()
        
        # Get HuggingFace-based classification result
        hf_result = (None, 0.0)
        if self.use_hf and self.hf_detector is not None:
            hf_pose_name, hf_confidence = self.classify_pose(img)
            hf_result = (hf_pose_name, hf_confidence)
            
            # If HF detects balasana when we're looking for balasana, log it
            if self.pose_name == 'balasana' and hf_pose_name == 'balasana':
                print("Successfully identified balasana pose!")
        
        # Combine results for final decision
        is_correct = False
        
        # If we're using HF detection and it correctly identified the expected pose with good confidence
        if self.use_hf and hf_result[0] == self.pose_name and hf_result[1] >= 0.8:
            is_correct = True
        # Or if angle-based detection is positive and we're not using HF
        elif angle_result and not self.use_hf:
            is_correct = True
        # If both detection methods partially agree, accept the pose
        elif angle_result and self.use_hf and hf_result[1] >= 0.6:
            is_correct = True
        
        # Draw status on image if requested
        if draw:
            color = (0, 255, 0) if is_correct else (0, 0, 255)
            cv2.putText(img, f"Correct: {is_correct}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, color, 2)
            
            if self.use_hf:
                cv2.putText(img, f"Pose: {hf_result[0]} ({hf_result[1]:.2f})", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        return is_correct, angle_result, hf_result, img