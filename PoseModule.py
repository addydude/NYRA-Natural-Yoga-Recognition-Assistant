import cv2
import mediapipe as mp
import time
import math
import numpy as np
import os
import pygame  # For audio playback


class PoseDetector:
    def __init__(self, mode = False, maxHands=1, modelComplexity=1, upBody = False, smooth=True, detectionCon = 0.5, trackCon = 0.5, pose_name="vrksana"):

        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplexity
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.pose_name = pose_name

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode,self.maxHands, self.modelComplex,  self.upBody, self.smooth, self.detectionCon, self.trackCon)
        
        # Define breathing patterns for different yoga poses
        self.breathing_patterns = {
            # Format: 'pose_name': (total_cycle_seconds, inhale_ratio)
            'vrksana': (6, 0.4),       # Tree pose: 2.4s inhale, 3.6s exhale
            'adhomukha': (8, 0.5),     # Downward dog: 4s inhale, 4s exhale 
            'balasana': (10, 0.3),     # Child's pose: 3s inhale, 7s exhale (more relaxed)
            'tadasan': (5, 0.5),       # Mountain pose: 2.5s inhale, 2.5s exhale
            'trikonasana': (7, 0.4),   # Triangle pose: 2.8s inhale, 4.2s exhale
            'virabhadrasana': (6, 0.45), # Warrior pose: 2.7s inhale, 3.3s exhale
            'bhujangasana': (7, 0.4),   # Cobra pose: 2.8s inhale, 4.2s exhale
            'setubandhasana': (8, 0.4), # Bridge pose: 3.2s inhale, 4.8s exhale
            'uttanasana': (6, 0.3),     # Standing forward bend: 1.8s inhale, 4.2s exhale
            'shavasana': (12, 0.3),     # Corpse pose: 3.6s inhale, 8.4s exhale (deeply relaxing)
            'ardhamatsyendrasana': (7, 0.4) # Half lord of the fishes pose: 2.8s inhale, 4.2s exhale
        }
        
        # Get breathing pattern for current pose
        breathing_pattern = self.breathing_patterns.get(self.pose_name, (6, 0.4))  # Default to vrksana pattern
        
        # Breathing guidance parameters
        self.breathing_start_time = time.time()
        self.breathing_cycle = breathing_pattern[0]  # Total breathing cycle in seconds
        self.inhale_ratio = breathing_pattern[1]     # Ratio of inhale time to total cycle
        self.is_inhaling = True   # Start with inhale
        self.prev_is_inhaling = True  # Track previous state for audio cue triggering
        
        # Initialize audio cues
        self.audio_initialized = False
        try:
            pygame.mixer.init()
            # Fix the path to correctly point to the static/audio directory
            audio_dir = os.path.join(os.path.dirname(__file__), 'static', 'audio')
            self.inhale_sound = os.path.join(audio_dir, 'inhale.mp3')
            self.exhale_sound = os.path.join(audio_dir, 'exhale.mp3')
            
            # Create directory if it doesn't exist
            if not os.path.exists(audio_dir):
                os.makedirs(audio_dir)
            
            # Create default audio files if they don't exist
            if not os.path.exists(self.inhale_sound) or not os.path.exists(self.exhale_sound):
                try:
                    from gtts import gTTS
                    
                    if not os.path.exists(self.inhale_sound):
                        tts = gTTS("Inhale deeply through your nose", lang='en')
                        tts.save(self.inhale_sound)
                        
                    if not os.path.exists(self.exhale_sound):
                        tts = gTTS("Exhale slowly through your mouth", lang='en')
                        tts.save(self.exhale_sound)
                except Exception as e:
                    print(f"Warning: Could not create audio files: {str(e)}")
                    
            self.audio_initialized = True
            print("Audio guidance initialized successfully")
        except Exception as e:
            print(f"Audio initialization failed: {str(e)}")
            self.audio_initialized = False

    def setPose(self, pose_name):
        """Update the pose name and adjust breathing pattern accordingly"""
        if pose_name != self.pose_name and pose_name in self.breathing_patterns:
            self.pose_name = pose_name
            breathing_pattern = self.breathing_patterns.get(self.pose_name, (6, 0.4))
            self.breathing_cycle = breathing_pattern[0]
            self.inhale_ratio = breathing_pattern[1]
            self.breathing_start_time = time.time()  # Reset the breathing timing
            print(f"Pose updated to {pose_name} with breathing cycle: {self.breathing_cycle}s")
            return True
        return False

    def findPose(self, img, draw=True):
        """
        Find and draw pose landmarks on the image
        Returns the image with pose landmarks drawn if draw=True
        """
        if img is None or img.size == 0:
            print("Warning: Empty image passed to findPose")
            return None
        
        # Ensure contiguous memory layout to prevent OpenCV stride errors
        if not img.flags['C_CONTIGUOUS']:
            img = np.ascontiguousarray(img)
        
        try:
            # Create a copy to avoid modifying the original
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.results = self.pose.process(imgRGB)
            
            if self.results.pose_landmarks:
                if draw:
                    # Create a fresh copy for drawing to prevent stride issues
                    draw_img = img.copy()
                    self.mpDraw.draw_landmarks(
                        draw_img, 
                        self.results.pose_landmarks,
                        self.mpPose.POSE_CONNECTIONS,
                        self.mpDraw.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                        self.mpDraw.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                    )
                    # Ensure result is contiguous
                    return np.ascontiguousarray(draw_img)
            
            # Return the original image if no drawing or no landmarks
            return np.ascontiguousarray(img)
            
        except Exception as e:
            print(f"Error in findPose: {e}")
            # Return the original image on error
            return img

    def getPosition(self, img, draw=True):
        self.lmList = []
        
        # Ensure the image is properly formatted
        if img is None or img.size == 0:
            return self.lmList
            
        # Make sure we have a contiguous array
        if not img.flags['C_CONTIGUOUS']:
            img = np.ascontiguousarray(img)
        
        try:
            # Initialize results if not already done
            if not hasattr(self, 'results'):
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                self.results = self.pose.process(imgRGB)
                
            if self.results and self.results.pose_landmarks:
                h, w, c = img.shape
                for id, lm in enumerate(self.results.pose_landmarks.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.lmList.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        except Exception as e:
            print(f"Error in getPosition: {e}")
            
        return self.lmList

    def findAngle(self, img, p1, p2, p3, draw=True):
        try:
            # Make sure lmList has enough points and valid indices
            if len(self.lmList) <= max(p1, p2, p3):
                print(f"Warning: Not enough landmarks for points {p1}, {p2}, {p3}")
                return 0
                
            # Finding the landmarks
            x1, y1 = self.lmList[p1][1:]
            x2, y2 = self.lmList[p2][1:]
            x3, y3 = self.lmList[p3][1:]

            # Calculating the angle between those landmarks
            angle = math.degrees(math.atan2(y3-y2, x3-x2) - 
                                math.atan2(y1-y2, x1-x2))
            
            if angle < 0:
                angle += 360
            
            # Only print angle if in reasonable range (avoid spam)
            if 0 <= angle <= 360:
                print(f"Angle {p1}-{p2}-{p3}: {angle:.1f}")

            if draw and img is not None and img.size > 0:
                # Make sure we have a contiguous array before drawing
                if not img.flags['C_CONTIGUOUS']:
                    img = np.ascontiguousarray(img)
                    
                # Draw points and angle
                cv2.circle(img, (x1, y1), 5, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 5, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (x3, y3), 5, (255, 0, 0), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
                cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 2)
                cv2.putText(img, str(int(angle)), (x2-50, y2+50),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                
            return angle
            
        except Exception as e:
            print(f"Error in findAngle: {e}")
            return 0

    def showBreathingGuide(self, img):
        """Display breathing guidance (inhale/exhale) on the image with audio cues"""
        # Check if image is valid
        if img is None or img.size == 0:
            print("Warning: Invalid image passed to showBreathingGuide")
            return None
            
        # Ensure contiguous memory layout
        if not img.flags['C_CONTIGUOUS']:
            img = np.ascontiguousarray(img)
            
        try:
            h, w, c = img.shape
            current_time = time.time()
            elapsed_time = current_time - self.breathing_start_time
            
            # Reset cycle when complete
            if elapsed_time >= self.breathing_cycle:
                self.breathing_start_time = current_time
                elapsed_time = 0
            
            # Determine if inhaling or exhaling based on position in cycle
            self.is_inhaling = elapsed_time < (self.breathing_cycle * self.inhale_ratio)
            
            # Play audio cue when transitioning between inhale and exhale
            if self.audio_initialized and self.is_inhaling != self.prev_is_inhaling:
                try:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                    pygame.mixer.music.load(self.inhale_sound if self.is_inhaling else self.exhale_sound)
                    pygame.mixer.music.play()
                except Exception as e:
                    print(f"Audio playback error: {str(e)}")
            
            # Update previous state
            self.prev_is_inhaling = self.is_inhaling
            
            # Calculate progress percentage through current breath phase
            if self.is_inhaling:
                progress = elapsed_time / (self.breathing_cycle * self.inhale_ratio)
            else:
                progress = (elapsed_time - self.breathing_cycle * self.inhale_ratio) / (self.breathing_cycle * (1 - self.inhale_ratio))
            
            # Limit progress to range [0, 1]
            progress = max(0, min(1, progress))
            
            # Create a fresh copy of the image for overlay
            overlay = img.copy()
            
            # Position and size of breathing indicator
            box_width = 300
            box_height = 100
            box_x = w - box_width - 20
            box_y = 20
            
            # Draw background box with rounded corners
            cv2.rectangle(overlay, (box_x, box_y), (box_x + box_width, box_y + box_height), (255, 255, 255), -1)
            
            # Text to display
            text = "INHALE" if self.is_inhaling else "EXHALE"
            text_color = (0, 128, 0) if self.is_inhaling else (128, 0, 0)  # Darker Green/Red for better contrast
            
            # Draw text centered in box
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 2)[0]
            text_x = box_x + (box_width - text_size[0]) // 2
            text_y = box_y + (box_height + text_size[1]) // 2
            cv2.putText(overlay, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, text_color, 2)
            
            # Add current pose name
            pose_text = f"Pose: {self.pose_name.capitalize()}"
            pose_text_size = cv2.getTextSize(pose_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0]
            pose_text_x = box_x + (box_width - pose_text_size[0]) // 2
            pose_text_y = box_y + 25
            cv2.putText(overlay, pose_text, (pose_text_x, pose_text_y), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 1)
            
            # Progress bar with smoother look
            bar_height = 15
            bar_y = box_y + box_height - bar_height - 10
            # Background of bar (light gray)
            cv2.rectangle(overlay, (box_x + 10, bar_y), (box_x + box_width - 10, bar_y + bar_height), 
                        (220, 220, 220), -1)
            # Filled portion of bar
            cv2.rectangle(overlay, (box_x + 10, bar_y), 
                        (int(box_x + 10 + progress * (box_width - 20)), bar_y + bar_height), 
                        text_color, -1)
            
            # Apply overlay with transparency - ensure result is contiguous
            alpha = 0.8  # Slightly more opaque for better visibility
            result = np.zeros_like(img)
            cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, result)
            
            return np.ascontiguousarray(result)
            
        except Exception as e:
            print(f"Error in showBreathingGuide: {e}")
            return img
    
    def checkVisibleParts(self, img):
        """
        Determine if key body parts (arms, legs) are visible in the current frame.
        Returns a dictionary with visibility status for each part.
        """
        visibility = {
            'right_arm': False,
            'left_arm': False,
            'right_leg': False,
            'left_leg': False
        }
        
        # If we don't have landmarks or results is None, return all as not visible
        if not hasattr(self, 'results') or not self.results.pose_landmarks:
            return visibility
            
        h, w, c = img.shape
        landmarks = self.results.pose_landmarks.landmark
        
        # Check right arm visibility (landmarks 12, 14, 16)
        if (landmarks[12].visibility > 0.7 and 
            landmarks[14].visibility > 0.7 and 
            landmarks[16].visibility > 0.7):
            visibility['right_arm'] = True
        
        # Check left arm visibility (landmarks 11, 13, 15)
        if (landmarks[11].visibility > 0.7 and 
            landmarks[13].visibility > 0.7 and 
            landmarks[15].visibility > 0.7):
            visibility['left_arm'] = True
        
        # Check right leg visibility (landmarks 24, 26, 28)
        if (landmarks[24].visibility > 0.7 and 
            landmarks[26].visibility > 0.7 and 
            landmarks[28].visibility > 0.7):
            visibility['right_leg'] = True
        
        # Check left leg visibility (landmarks 23, 25, 27)
        if (landmarks[23].visibility > 0.7 and 
            landmarks[25].visibility > 0.7 and 
            landmarks[27].visibility > 0.7):
            visibility['left_leg'] = True
            
        return visibility


def main():
    cap = cv2.VideoCapture('videos/a.mp4')
    pTime = 0
    detector = PoseDetector()
    while True:
        success, img = cap.read()
        img = detector.findPose(img)
        lmList = detector.getPosition(img)
        
        # Add breathing guide
        if len(lmList) > 0:  # Only show breathing guide when a person is detected
            img = detector.showBreathingGuide(img)
        
        print(lmList)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)



if __name__ == "__main__":
    main()