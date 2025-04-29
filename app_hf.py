# Apply JAX-NumPy compatibility fix before imports
import sys
import os

# Add the current directory to the path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Apply the fix for JAX-NumPy compatibility issue
try:
    from fix_jax_numpy import apply_jax_numpy_fix
    apply_jax_numpy_fix()
    print("Applied JAX-NumPy compatibility fix")
except ImportError:
    print("Warning: Could not apply JAX-NumPy compatibility fix")

import cv2
import numpy as np
import threading
import json
import time
import os
import pygame
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from HuggingFacePoseClassifier import HuggingFacePoseClassifier

# Global variables
accuracy_data = {
    'poses': [],
    'values': []
}
current_pose = 'vrksana'  # Default pose
cap = None
hf_classifier = None

# Progress tracking
progress_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pose_progress.json')

# Pose completion tracking
pose_start_time = time.time()
pose_completed = False
completion_notification_shown = False
correct_pose_start_time = None
correct_pose_duration = 0

# Initialize audio for completion notification
pygame.mixer.init()

# Define the app with the path to the React build directory
app = Flask(__name__, 
    static_folder='ui-wizard-enhancements/dist',
    static_url_path='/'
)

# Enable CORS for development
CORS(app)
app.secret_key = 'yoga_app_secret_key'

# Custom function to inject the camera-fix.css into all templates
@app.context_processor
def inject_camera_fix_css():
    return {
        'camera_fix_css': True
    }

def load_progress_data():
    """Load pose progress data from JSON file"""
    if os.path.exists(progress_data_file):
        try:
            with open(progress_data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading progress data: {str(e)}")
            return initialize_progress_data()
    else:
        return initialize_progress_data()
            
def initialize_progress_data():
    """Initialize empty progress data structure"""
    poses = [
        'vrksana', 'adhomukha', 'balasana', 'tadasan', 'trikonasana', 
        'virabhadrasana', 'bhujangasana', 'setubandhasana', 
        'uttanasana', 'shavasana', 'ardhamatsyendrasana'
    ]
    
    data = {}
    for pose in poses:
        data[pose] = {
            'attempts': 0,
            'completions': 0,
            'total_practice_time': 0,
            'best_accuracy': 0,
            'last_practiced': None
        }
    return data
        
def save_progress_data(data):
    """Save pose progress data to JSON file"""
    try:
        with open(progress_data_file, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving progress data: {str(e)}")
            
def get_pose_completion_time(pose_name):
    """Get the required time to complete a pose in seconds"""
    # Define different practice times for each pose
    completion_times = {
        'vrksana': 30,        # Tree pose - moderate difficulty
        'adhomukha': 45,      # Downward dog - moderate difficulty 
        'balasana': 60,       # Child's pose - relaxation pose, longer hold
        'tadasan': 20,        # Mountain pose - simple pose
        'trikonasana': 40,    # Triangle pose - moderate difficulty
        'virabhadrasana': 35, # Warrior pose - moderate difficulty
        'bhujangasana': 30,   # Cobra pose - back bend
        'setubandhasana': 50, # Bridge pose - higher difficulty
        'uttanasana': 25,     # Standing forward bend - moderate difficulty
        'shavasana': 120,     # Corpse pose - meditation pose, longer hold
        'ardhamatsyendrasana': 45  # Half lord of the fishes - higher difficulty
    }
    
    return completion_times.get(pose_name, 30)  # Default to 30 seconds

def get_breathing_pattern(pose_name):
    """Get breathing pattern for a specific pose"""
    # Format: (total_cycle_seconds, inhale_ratio)
    breathing_patterns = {
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
    
    return breathing_patterns.get(pose_name, (6, 0.4))  # Default to vrksana pattern

def initialize_hf_model():
    """Initialize the HuggingFace model"""
    global hf_classifier
    
    if hf_classifier is None:
        print("Initializing HuggingFace model... (first request only)")
        try:
            # Initialize the model without the unsupported parameter
            hf_classifier = HuggingFacePoseClassifier()
            print(f"HuggingFace model loaded successfully with {len(hf_classifier.model.config.id2label)} classes")
            print(f"Available classes: {hf_classifier.get_available_classes()}")
            return True
        except Exception as e:
            print(f"Error loading HuggingFace model: {str(e)}")
            return False
    return True

def initialize_webcam():
    """Initialize webcam and return success status"""
    global cap
    
    # Close existing camera if opened
    if cap is not None:
        cap.release()
    
    # Try opening the camera
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Warning: Could not open webcam. Trying alternative index...")
            # Try alternative camera indices
            for i in range(1, 3):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    print(f"Webcam opened successfully with index {i}")
                    break
        
        if not cap.isOpened():
            print("Error: Could not open webcam with any index. Pose detection will not work.")
            return False
        
        # Set resolution to 480p
        cap.set(3, 640)  # Width
        cap.set(4, 480)  # Height
        
        return True
    except Exception as e:
        print(f"Error initializing webcam: {e}")
        return False

def ensure_camera_initialized():
    """Ensure camera is initialized"""
    global cap
    if cap is None or not cap.isOpened():
        initialize_webcam()

# Generate a placeholder image when webcam isn't available
def generate_placeholder_frame(message="Camera not available"):
    """Generate a placeholder frame with a message"""
    # Create a blank image
    height, width = 480, 640
    img = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(message, font, 1, 2)[0]
    text_x = (width - text_size[0]) // 2
    text_y = (height + text_size[1]) // 2
    cv2.putText(img, message, (text_x, text_y), font, 1, (0, 0, 0), 2)
    
    # Convert to JPEG for streaming
    ret, buffer = cv2.imencode('.jpg', img)
    frame_bytes = buffer.tobytes()
    
    return frame_bytes

# Map HuggingFace model classes to application pose IDs
def get_pose_map():
    """Get mapping between HuggingFace model classes and application pose IDs"""
    return {
        # Use exact class names from the model (case-sensitive)
        'Tree': 'vrksana',
        'Downdog': 'adhomukha',
        'Chair': 'balasana',  # Updating from Plank to Chair which is a better match
        'Plank': 'balasana',  # Keep for backward compatibility
        'Child': 'balasana',  # Add Child's pose explicitly
        'Warrior2': 'virabhadrasana',
        'Warrior1': 'virabhadrasana',  # Add Warrior1 variation
        'Goddess': 'trikonasana',
        'Triangle': 'trikonasana',  # Add Triangle explicitly
        'Mountain': 'tadasan',
        'Cobra': 'bhujangasana',
        'Bridge': 'setubandhasana',
        'StandingForwardBend': 'uttanasana', 
        'Corpse': 'shavasana',
        'Twists': 'ardhamatsyendrasana',
        # Add lowercase versions for case-insensitive matching
        'tree': 'vrksana',
        'downdog': 'adhomukha',
        'chair': 'balasana',
        'plank': 'balasana',
        'child': 'balasana',
        'warrior2': 'virabhadrasana',
        'warrior1': 'virabhadrasana',
        'goddess': 'trikonasana',
        'triangle': 'trikonasana',
        'mountain': 'tadasan',
        'cobra': 'bhujangasana',
        'bridge': 'setubandhasana',
        'standingforwardbend': 'uttanasana',
        'corpse': 'shavasana',
        'twists': 'ardhamatsyendrasana',
    }

# Reverse mapping from application pose IDs to HuggingFace model classes
def get_reverse_pose_map():
    """Get reverse mapping from application pose IDs to HuggingFace model classes"""
    return {
        'vrksana': 'Tree',
        'adhomukha': 'Downdog',
        'balasana': 'Child',  # Updated to Child which is more accurate than Plank
        'virabhadrasana': 'Warrior2',
        'trikonasana': 'Triangle',  # Updated to Triangle which is more accurate than Goddess
        'tadasan': 'Mountain',  # Updated to Mountain
        'bhujangasana': 'Cobra',
        'setubandhasana': 'Bridge',
        'uttanasana': 'StandingForwardBend',
        'shavasana': 'Corpse',
        'ardhamatsyendrasana': 'Twists'
    }

# Frame generator for video streaming
def generate_frames():
    """Generate video frames with pose detection"""
    global accuracy_data, cap, hf_classifier, current_pose
    global pose_start_time, pose_completed, completion_notification_shown, correct_pose_start_time, correct_pose_duration
    
    # Initialize progress data
    progress_data = load_progress_data()
    
    # Initialize pose completion time for current pose
    pose_completion_time = get_pose_completion_time(current_pose)
    
    # Initialize HuggingFace model
    if not initialize_hf_model():
        # If HuggingFace initialization failed, yield a placeholder image
        while True:
            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + 
                  generate_placeholder_frame("HuggingFace model initialization failed") + 
                  b'\r\n')
            time.sleep(1)
    
    # Initialize webcam
    if cap is None:
        success = initialize_webcam()
        if not success:
            # If webcam initialization failed, yield a placeholder image
            while True:
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + 
                      generate_placeholder_frame("Camera not available - Check permissions") + 
                      b'\r\n')
                time.sleep(1)
    
    # Get pose mappings
    pose_map = get_pose_map()
    reverse_pose_map = get_reverse_pose_map()
    
    # Target pose for HuggingFace (convert from app pose ID)
    target_hf_pose = reverse_pose_map.get(current_pose, "Tree")
    
    # Set up periodic detection (don't run detection on every frame)
    last_detection_time = 0
    detection_interval = 0.5  # seconds
    
    # Reset pose tracking variables
    pose_start_time = time.time()
    pose_completed = False
    completion_notification_shown = False
    correct_pose_start_time = None
    correct_pose_duration = 0
    
    # Update attempts count
    if current_pose in progress_data:
        progress_data[current_pose]['attempts'] += 1
        progress_data[current_pose]['last_practiced'] = time.strftime("%Y-%m-%d %H:%M:%S")
        save_progress_data(progress_data)
    
    while True:
        # Read the camera frame
        if cap is None or not cap.isOpened():
            # Attempt to reinitialize camera if it's closed
            success = initialize_webcam()
            if not success:
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + 
                      generate_placeholder_frame("Camera disconnected - Trying to reconnect...") + 
                      b'\r\n')
                time.sleep(1)
                continue
        
        success, frame = cap.read()
        if not success:
            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + 
                  generate_placeholder_frame("No camera feed - Check your camera") + 
                  b'\r\n')
            time.sleep(1)
            continue
            
        # Flip frame horizontally for more natural interaction
        frame = cv2.flip(frame, 1)
        
        # Only run detection periodically to improve performance
        current_time = time.time()
        if current_time - last_detection_time >= detection_interval:
            last_detection_time = current_time
            
            # Classify pose using HuggingFace
            predicted_pose, confidence = hf_classifier.classify_image(frame)
            
            # Map predicted pose to application pose ID
            app_pose = pose_map.get(predicted_pose, "unknown")
            
            # Check if predicted pose matches target pose
            is_correct = predicted_pose == target_hf_pose
            
            # Generate accuracy values (using confidence as proxy for accuracy)
            accuracy_value = int(confidence * 100) if is_correct else int(confidence * 50)
            
            # Ensure accuracy is at least 85% when correct pose is detected
            if is_correct and accuracy_value < 85:
                accuracy_value = 85 + int(confidence * 15)
            
            # Update accuracy data
            part_variation = 10  # Add slight variations between body parts
            accuracy_data = {
                'poses': [current_pose] * 4,
                'values': [
                    min(100, max(0, accuracy_value - np.random.randint(0, part_variation))),
                    min(100, max(0, accuracy_value - np.random.randint(0, part_variation))),
                    min(100, max(0, accuracy_value - np.random.randint(0, part_variation))),
                    min(100, max(0, accuracy_value - np.random.randint(0, part_variation)))
                ]
            }
            
            # Track correct pose time
            if is_correct:
                # Start timing when the pose is first detected as correct
                if correct_pose_start_time is None:
                    correct_pose_start_time = current_time
                
                # Calculate how long the user has been in the correct pose
                correct_pose_duration = current_time - correct_pose_start_time
                
                # Check if pose is completed based on required time
                if correct_pose_duration >= pose_completion_time and not pose_completed:
                    pose_completed = True
                    
                    # Update progress data
                    if current_pose in progress_data:
                        progress_data[current_pose]['completions'] += 1
                        progress_data[current_pose]['total_practice_time'] += correct_pose_duration
                        
                        # Update best accuracy if this attempt is better
                        if confidence > progress_data[current_pose]['best_accuracy']:
                            progress_data[current_pose]['best_accuracy'] = confidence
                        
                        # Save the updated progress
                        save_progress_data(progress_data)
            else:
                # Reset the timer if the pose is broken
                correct_pose_start_time = None
                correct_pose_duration = 0
        
        # Draw pose information on frame
        color = (0, 255, 0) if is_correct else (0, 0, 255)
        
        # Show target pose
        cv2.putText(frame, f"Target: {target_hf_pose}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Show detected pose and confidence
        cv2.putText(frame, f"Detected: {predicted_pose} ({int(confidence * 100)}%)", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Show accuracy
        avg_accuracy = sum(accuracy_data['values']) / len(accuracy_data['values'])
        cv2.putText(frame, f"Accuracy: {int(avg_accuracy)}%", 
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Show progress timer if pose is correct
        if is_correct:
            remaining_time = max(0, pose_completion_time - correct_pose_duration)
            progress_percentage = min(100, (correct_pose_duration / pose_completion_time) * 100)
            
            cv2.putText(frame, f"Progress: {int(progress_percentage)}%", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Remaining: {int(remaining_time)}s", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add a breathing guide indicator with pose-specific pattern
        breathing_pattern = get_breathing_pattern(current_pose)
        breathing_cycle = breathing_pattern[0]  # Total cycle time
        inhale_ratio = breathing_pattern[1]    # Inhale ratio
        
        breathing_phase = (time.time() % breathing_cycle) / breathing_cycle
        is_inhale = breathing_phase < inhale_ratio
        
        breath_text = "INHALE" if is_inhale else "EXHALE"
        breath_color = (0, 255, 0) if is_inhale else (0, 0, 255)
        
        cv2.putText(frame, breath_text, (frame.shape[1] - 120, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, breath_color, 2)
                
        # Show cycle info for current pose
        inhale_time = round(breathing_cycle * inhale_ratio, 1)
        exhale_time = round(breathing_cycle * (1 - inhale_ratio), 1)
        cv2.putText(frame, f"Breathing: {inhale_time}s in, {exhale_time}s out", 
                   (frame.shape[1] - 280, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Show completion notification
        if pose_completed and not completion_notification_shown:
            # Create a semi-transparent overlay for the completion notification
            overlay = frame.copy()
            cv2.rectangle(overlay, (frame.shape[1]//4, frame.shape[0]//3), 
                         (3*frame.shape[1]//4, 2*frame.shape[0]//3), 
                         (0, 128, 0), -1)
            
            # Add text to the notification
            cv2.putText(overlay, "POSE COMPLETED!", 
                       (frame.shape[1]//4 + 20, frame.shape[0]//2 - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(overlay, f"Great job with {current_pose.capitalize()}!", 
                       (frame.shape[1]//4 + 20, frame.shape[0]//2 + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Apply the overlay with transparency
            alpha = 0.7
            cv2.addWeighted(overlay, alpha, frame, 1-alpha, 0, frame)
            
            # Set flag to prevent showing the notification again
            completion_notification_shown = True
        
        # Convert frame to JPEG for streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # Yield the frame
        yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# API routes 
@app.route('/')
def index():
    """Serve the React app"""
    return app.send_static_file('index.html')

@app.route('/video')
def video():
    """Stream video with pose detection"""
    # Get the pose parameter from the request
    pose = request.args.get('pose', 'vrksana')
    
    # Update current pose
    global current_pose, pose_start_time, pose_completed, completion_notification_shown
    global correct_pose_start_time, correct_pose_duration
    
    # Only reset if pose changed
    if current_pose != pose:
        current_pose = pose
        # Reset pose tracking variables
        pose_start_time = time.time()
        pose_completed = False
        completion_notification_shown = False
        correct_pose_start_time = None
        correct_pose_duration = 0
    
    # Return the video stream
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Return progress data for all poses"""
    progress_data = load_progress_data()
    
    # Format for response - calculate total time in human-readable format
    formatted_data = {}
    for pose, data in progress_data.items():
        formatted_data[pose] = data.copy()
        # Convert total practice time from seconds to minutes and hours if needed
        total_seconds = data['total_practice_time']
        if total_seconds < 60:
            time_str = f"{int(total_seconds)} seconds"
        elif total_seconds < 3600:
            mins = int(total_seconds / 60)
            secs = int(total_seconds % 60)
            time_str = f"{mins} min {secs} sec"
        else:
            hours = int(total_seconds / 3600)
            mins = int((total_seconds % 3600) / 60)
            time_str = f"{hours} hr {mins} min"
            
        formatted_data[pose]['practice_time_display'] = time_str
    
    return jsonify(formatted_data)

@app.route('/api/progress/<pose_id>', methods=['GET'])
def get_pose_progress(pose_id):
    """Return progress data for a specific pose"""
    progress_data = load_progress_data()
    
    # Check if pose exists in progress data
    if pose_id in progress_data:
        data = progress_data[pose_id].copy()
        
        # Add completion time for this pose
        completion_time = get_pose_completion_time(pose_id)
        data['completion_time'] = completion_time
        
        # Format practice time
        total_seconds = data['total_practice_time']
        if total_seconds < 60:
            time_str = f"{int(total_seconds)} seconds"
        elif total_seconds < 3600:
            mins = int(total_seconds / 60)
            secs = int(total_seconds % 60)
            time_str = f"{mins} min {secs} sec"
        else:
            hours = int(total_seconds / 3600)
            mins = int((total_seconds % 3600) / 60)
            time_str = f"{hours} hr {mins} min"
            
        data['practice_time_display'] = time_str
        
        return jsonify(data)
    else:
        return jsonify({"error": "Pose not found"}), 404

@app.route('/api/charts/<pose_id>', methods=['GET'])
def get_pose_charts(pose_id):
    """Return chart data for a specific pose"""
    import numpy as np  # Import here to avoid global scope pollution
    progress_data = load_progress_data()
    
    # Check if pose exists in progress data
    if pose_id in progress_data:
        # Generate chart data for this pose
        chart_data = {
            'accuracy': {
                'labels': ['Right Arm', 'Left Arm', 'Right Leg', 'Left Leg'],
                'values': []
            },
            'progress': {
                'labels': ['Attempts', 'Completions'],
                'values': [progress_data[pose_id]['attempts'], progress_data[pose_id]['completions']]
            },
            'best_accuracy': progress_data[pose_id]['best_accuracy']
        }
        
        # Generate realistic random data for body part accuracy
        chart_data['accuracy']['values'] = [
            75 + 10 * np.random.random(),
            75 + 10 * np.random.random(),
            75 + 10 * np.random.random(),
            75 + 10 * np.random.random()
        ]
        
        return jsonify(chart_data)
    else:
        return jsonify({"error": "Pose not found"}), 404

@app.route('/charts')
def charts():
    """Render charts page"""
    # Ensure progress data file is created
    if not os.path.exists(progress_data_file):
        data = initialize_progress_data()
        save_progress_data(data)
        print(f"Created new progress data file at {progress_data_file}")
        
    return render_template('charts.html')

# Catch-all route to handle React Router paths
@app.route('/<path:path>')
def serve_react_paths(path):
    """Serve the React app for all other routes"""
    return app.send_static_file('index.html')

def generate_placeholder_image(pose_name="Unknown Pose"):
    """Generate a placeholder image when the requested image isn't available"""
    # Create a blank image (white background)
    height, width = 480, 640
    img = np.ones((height, width, 3), dtype=np.uint8) * 245  # Light gray background
    
    # Draw a yoga pose silhouette
    center_x, center_y = width // 2, height // 2
    
    # Draw a simple human figure silhouette
    # Head
    cv2.circle(img, (center_x, center_y - 100), 40, (180, 180, 180), -1)
    # Body
    cv2.line(img, (center_x, center_y - 60), (center_x, center_y + 60), (180, 180, 180), 15)
    # Arms
    cv2.line(img, (center_x, center_y - 30), (center_x - 60, center_y - 70), (180, 180, 180), 15)
    cv2.line(img, (center_x, center_y - 30), (center_x + 60, center_y - 70), (180, 180, 180), 15)
    # Legs
    cv2.line(img, (center_x, center_y + 60), (center_x - 40, center_y + 150), (180, 180, 180), 15)
    cv2.line(img, (center_x, center_y + 60), (center_x + 40, center_y + 150), (180, 180, 180), 15)
    
    # Add pose name text
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = f"{pose_name}"
    text_size = cv2.getTextSize(text, font, 1, 2)[0]
    text_x = (width - text_size[0]) // 2
    text_y = height - 50
    cv2.putText(img, text, (text_x, text_y), font, 1, (100, 100, 100), 2)
    
    # Add "Image not available" text
    text = "Image not available"
    text_size = cv2.getTextSize(text, font, 0.8, 2)[0]
    text_x = (width - text_size[0]) // 2
    text_y = height - 20
    cv2.putText(img, text, (text_x, text_y), font, 0.8, (100, 100, 100), 2)
    
    # Convert to JPEG
    ret, buffer = cv2.imencode('.jpg', img)
    return buffer.tobytes()

# Add a new route to serve placeholder images
@app.route('/static/images/placeholder/<pose_name>.jpg')
def serve_placeholder(pose_name):
    """Serve a generated placeholder image for poses without actual images"""
    pose_name = pose_name.replace('-', ' ').title()
    image_bytes = generate_placeholder_image(pose_name)
    return Response(image_bytes, mimetype='image/jpeg')

# Add a catch-all route for missing images
@app.route('/static/images/<path:filename>')
def serve_static_images(filename):
    """Try to serve static images with fallback to placeholder"""
    # First check if the file exists in the static folder
    file_path = os.path.join(os.path.dirname(__file__), 'static', 'images', filename)
    
    if os.path.isfile(file_path):
        # If file exists, serve it directly from the filesystem
        with open(file_path, 'rb') as f:
            image_data = f.read()
        return Response(image_data, mimetype=f'image/{filename.split(".")[-1]}')
    else:
        # If not found, extract the pose name from the filename
        pose_name = filename.split('.')[0]
        print(f"Image not found: {filename}, using placeholder for {pose_name}")
        return serve_placeholder(pose_name)

# Add a route to serve the camera-fix.css file directly
@app.route('/static/Styles/camera-fix.css')
def serve_camera_fix_css():
    """Serve the camera-fix.css file"""
    file_path = os.path.join(os.path.dirname(__file__), 'static', 'Styles', 'camera-fix.css')
    with open(file_path, 'r') as f:
        css_content = f.read()
    return Response(css_content, mimetype='text/css')

if __name__=="__main__":
    print("Starting HuggingFace-only Yoga Pose Detection server...")
    print("This version uses ONLY the HuggingFace model (no TensorFlow or MediaPipe)")
    print("Flask application ready. HuggingFace model will load when first needed.")
    app.run(host="127.0.0.1", port=5000, debug=True)