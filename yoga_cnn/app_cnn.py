import cv2
import numpy as np
import os
import time
import pygame
from gtts import gTTS
from PoseClassifier import PoseClassifier

# Initialize pygame for audio
pygame.init()
pygame.mixer.init()

class YogaApp:
    def __init__(self):
        # Initialize the pose classifier
        self.pose_classifier = PoseClassifier()
        
        # Initialize breathing guide parameters
        self.breathing_guide = {
            "state": "inhale",  # Current breathing state (inhale/exhale)
            "counter": 0,       # Counter for current breath
            "duration": {       # Duration for each pose in seconds
                "inhale": {
                    "tadasana": 4,
                    "vrksana": 4,
                    "balasana": 3,
                    "trikonasana": 4,
                    "virabhadrasana": 5,
                    "adho_mukha": 4,
                    "default": 4
                },
                "exhale": {
                    "tadasana": 4,
                    "vrksana": 4,
                    "balasana": 5,
                    "trikonasana": 4,
                    "virabhadrasana": 5,
                    "adho_mukha": 6,
                    "default": 4
                }
            }
        }
        
        # Load audio files
        self.audio_files = {
            "inhale": r"D:\NYRAGGbackup - Copy\static\audio\inhale.mp3",
            "exhale": r"D:\NYRAGGbackup - Copy\static\audio\exhale.mp3"
        }
        
        # Check if audio files exist
        for key, path in self.audio_files.items():
            if not os.path.exists(path):
                # Generate audio files if they don't exist
                print(f"Generating {key} audio...")
                tts = gTTS(text=key, lang='en')
                os.makedirs(os.path.dirname(path), exist_ok=True)
                tts.save(path)
        
        # Variables for tracking
        self.prev_pose = None
        self.pose_start_time = time.time()
        self.last_feedback_time = 0
        self.feedback_interval = 5  # seconds
        self.last_breathing_cue = 0
    
    def update_breathing_guide(self, pose_name, current_time):
        """Update breathing guide state based on current pose"""
        if pose_name == "No person detected" or pose_name == "Unknown":
            return
        
        # Get breathing durations for this pose
        inhale_duration = self.breathing_guide["duration"]["inhale"].get(
            pose_name, self.breathing_guide["duration"]["inhale"]["default"]
        )
        exhale_duration = self.breathing_guide["duration"]["exhale"].get(
            pose_name, self.breathing_guide["duration"]["exhale"]["default"]
        )
        
        # Update breathing counter
        self.breathing_guide["counter"] += 1
        
        # Check if it's time to switch breathing state
        if self.breathing_guide["state"] == "inhale" and \
           current_time - self.last_breathing_cue >= inhale_duration:
            self.breathing_guide["state"] = "exhale"
            self.last_breathing_cue = current_time
            # Play exhale sound
            pygame.mixer.music.load(self.audio_files["exhale"])
            pygame.mixer.music.play()
        elif self.breathing_guide["state"] == "exhale" and \
             current_time - self.last_breathing_cue >= exhale_duration:
            self.breathing_guide["state"] = "inhale"
            self.last_breathing_cue = current_time
            # Play inhale sound
            pygame.mixer.music.load(self.audio_files["inhale"])
            pygame.mixer.music.play()
    
    def provide_feedback(self, pose_name, confidence, current_time):
        """Provide audio feedback based on pose and confidence"""
        if pose_name == "No person detected" or pose_name == "Unknown":
            return
        
        # Provide feedback at intervals if confidence is high enough
        if current_time - self.last_feedback_time > self.feedback_interval and confidence > 0.7:
            self.last_feedback_time = current_time
            
            # Generate feedback text based on pose
            if confidence > 0.9:
                feedback_text = f"Excellent! Your {pose_name} pose looks perfect."
            else:
                feedback_text = f"Good job! You're doing {pose_name} correctly."
            
            # Generate and play audio feedback
            tts = gTTS(feedback_text, lang='en')
            feedback_path = os.path.join(os.path.dirname(self.audio_files["inhale"]), "feedback.mp3")
            tts.save(feedback_path)
            pygame.mixer.music.load(feedback_path)
            pygame.mixer.music.play()
    
    def run(self):
        """Run the yoga application"""
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Failed to read from webcam")
                break
            
            # Get current time
            current_time = time.time()
            
            # Classify the pose
            pose_name, confidence, processed_frame = self.pose_classifier.classify_pose(frame, draw=True)
            
            # Update breathing guide
            self.update_breathing_guide(pose_name, current_time)
            
            # Provide feedback
            self.provide_feedback(pose_name, confidence, current_time)
            
            # Display the result on frame
            cv2.putText(processed_frame, f"Pose: {pose_name}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(processed_frame, f"Confidence: {confidence:.2f}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display breathing guide
            breathing_text = f"Breathing: {self.breathing_guide['state'].upper()}"
            cv2.putText(processed_frame, breathing_text, (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
            # Display time in pose if it hasn't changed
            if pose_name == self.prev_pose and pose_name != "No person detected":
                pose_duration = current_time - self.pose_start_time
                cv2.putText(processed_frame, f"Time in pose: {int(pose_duration)}s", (10, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                self.pose_start_time = current_time
                self.prev_pose = pose_name
            
            # Display the frame
            cv2.imshow('Yoga Pose Classification with CNN', processed_frame)
            
            # Break loop with 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Release resources
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = YogaApp()
    app.run()