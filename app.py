# Apply JAX-NumPy compatibility fix before imports
import sys
import os
import threading

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

from flask import Flask, render_template, Response, request, jsonify, send_from_directory
import numpy as np
import cv2
import time 
import PoseModule as pm
import matplotlib.pyplot as plt
import threading
import json
import pygame
from websocket_handler import start_websocket_server, broadcast_pose_status

# Import CORS to handle cross-origin requests during development
from flask_cors import CORS

# Initialize audio system
try:
    pygame.mixer.init()
    print("Audio system initialized successfully")
except Exception as e:
    print(f"Audio initialization warning: {str(e)}")

# Ensure audio directory exists
audio_dir = os.path.join(os.path.dirname(__file__), 'static', 'audio')
if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

# Check and generate audio files if needed
def ensure_audio_files():
    inhale_path = os.path.join(audio_dir, 'inhale.mp3')
    exhale_path = os.path.join(audio_dir, 'exhale.mp3')
    
    if not os.path.exists(inhale_path) or not os.path.exists(exhale_path):
        try:
            from gtts import gTTS
            
            if not os.path.exists(inhale_path):
                tts = gTTS("Inhale deeply", lang='en')
                tts.save(inhale_path)
                
            if not os.path.exists(exhale_path):
                tts = gTTS("Exhale slowly", lang='en')
                tts.save(exhale_path)
                
            print("Audio files created successfully")
        except Exception as e:
            print(f"Error creating audio files: {str(e)}")

# Run audio file setup in a background thread to avoid blocking app startup
threading.Thread(target=ensure_audio_files).start()

# Define the app with explicit static folder
app = Flask(__name__, 
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'),
    static_url_path='/static'
)

# Enable CORS for development
CORS(app)

# Global variable to store accuracy data
accuracy_data = {
    'poses': [],
    'values': []
}

# Global variables for pose tracking
current_pose = 'vrksana'  # Default to vrksana
pose_hold_start_time = None
pose_correct_duration = 0
pose_completed = False
correct_pose_threshold = 0.85  # 85% accuracy for pose to be considered correct

# Initialize webcam capture
cap = cv2.VideoCapture(0)

# Initialize the PoseDetector with default pose
detector = pm.PoseDetector(pose_name='vrksana')

# Import yoga pose angle data
try:
    from data import AngleData
    dataList = AngleData
except ImportError:
    # Define fallback data if import fails
    dataList = [
        {'Name': 'tadasan', 'right_arm': 201, 'left_arm': 162, 'right_leg':177,'left_leg':182},
        {'Name': 'vrksana', 'right_arm': 207, 'left_arm': 158, 'right_leg':180,'left_leg':329},
        {'Name': 'balasana', 'right_arm': 155, 'left_arm': 167, 'right_leg':337,'left_leg':335},
        {'Name': 'trikonasana', 'right_arm': 181, 'left_arm': 184, 'right_leg':176,'left_leg':182},
        {'Name': 'virabhadrasana', 'right_arm': 167, 'left_arm': 166, 'right_leg':273,'left_leg':178},
        {'Name': 'adhomukha', 'right_arm': 176, 'left_arm': 171, 'right_leg':177,'left_leg':179},
    ]

# Define required hold times in seconds for pose completion
pose_completion_times = {
    'vrksana': 30,        # Tree pose
    'adhomukha': 45,      # Downward dog
    'balasana': 60,       # Child's pose
    'tadasan': 20,        # Mountain pose
    'trikonasana': 40,    # Triangle pose
    'virabhadrasana': 35, # Warrior pose
    'bhujangasana': 40,   # Cobra pose
    'setubandhasana': 50, # Bridge pose
    'uttanasana': 35,     # Standing forward bend
    'shavasana': 120,     # Corpse pose
    'ardhamatsyendrasana': 45  # Half lord of the fishes
}

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Warning: Cannot open webcam! The application might not function correctly.")

def make_1080p():
    cap.set(3, 1920)
    cap.set(4, 1080)

def make_720p():
    cap.set(3, 1280)
    cap.set(4, 720)

def make_480p():
    cap.set(3, 640)
    cap.set(4, 480)

def change_res(width, height):
    cap.set(3, width)
    cap.set(4, height)

def get_pose_index(pose_name):
    """Get the index of the pose in dataList based on the pose name"""
    pose_indices = {
        'vrksana': 1,
        'balasana': 2, 
        'trikonasana': 3,
        'virabhadrasana': 4,
        'adhomukha': 5,
        'tadasan': 0  # Default
    }
    return pose_indices.get(pose_name, 0)  # Default to tadasan (0) if pose not found

def compare_right_arm(right_arm):
    # Get the pose data based on the current global pose
    pose_index = get_pose_index(current_pose)
    pose_data = [y for x, y in list(dataList[pose_index].items()) if type(y) == int]
    
    if right_arm <= pose_data[0]:
        acc = (right_arm / pose_data[0]) * 100
    else:
        acc = 0
        
    if abs(pose_data[0] - right_arm) <= 10:
        print("Your right arm is accurate")
    else:
        print("Your right arm is not accurate")

    return acc

def compare_left_arm(left_arm):
    # Get the pose data based on the current global pose
    pose_index = get_pose_index(current_pose)
    pose_data = [y for x, y in list(dataList[pose_index].items()) if type(y) == int]
    
    if left_arm <= pose_data[1]:
        acc = (left_arm / pose_data[1]) * 100
    else:
        acc = 0
        
    if abs(pose_data[1] - left_arm) <= 10:    
        print("Your left arm is accurate")  
    else:
        print("Your left arm is not accurate, try again")
    
    return acc
    
def compare_right_leg(right_leg):
    # Get the pose data based on the current global pose
    pose_index = get_pose_index(current_pose)
    pose_data = [y for x, y in list(dataList[pose_index].items()) if type(y) == int]

    if right_leg <= pose_data[2]:
        acc = (right_leg / pose_data[2]) * 100
    else:
        acc = 0

    if abs(pose_data[2] - right_leg) <= 10:
        print("Your right leg is accurate")
    else:
        print("Your right leg is not accurate, try again") 

    return acc
       
def compare_left_leg(left_leg):
    # Get the pose data based on the current global pose
    pose_index = get_pose_index(current_pose)
    pose_data = [y for x, y in list(dataList[pose_index].items()) if type(y) == int]
    
    if left_leg <= pose_data[3]:
        acc = (left_leg / pose_data[3]) * 100
    else:
        acc = 0

    if abs(pose_data[3] - left_leg) <= 10 and left_leg < pose_data[3]:
       print("Your left leg is accurate") 
    else:
        print("Your left leg is not accurate, try again") 
    
    return acc

arr = np.array([])
    
def generate_frames(arr):
    global accuracy_data, pose_hold_start_time, pose_correct_duration, pose_completed
    count = 0
    timeout = 20
    timeout_start = time.time()
    
    while time.time() < timeout_start + timeout:
        while True:
            ## read the camera frame
            success, frame = cap.read()
            if not success:
                break
                
            frame = cv2.flip(frame, 1)
      
            # resize the image
            img = frame.copy()
             
            # Use our PoseDetector - draw landmarks but don't show breathing guide inside camera view
            frame = detector.findPose(frame, draw=True)
            lmlist = detector.getPosition(frame, draw=False)
            
            # Get breathing info for external UI without drawing on camera frame
            breathing_info = detector.getBreathingInfo()
            
            # Check if we have a person in frame
            if len(lmlist) != 0:
                # Continue with angle-based measurements - all with draw=False to prevent extra blue lines
                RightArmAngle = int(detector.findAngle(frame, 12, 14, 16, draw=False))
                right_arm_accuracy = compare_right_arm(RightArmAngle)
                if (count <= 16 and right_arm_accuracy != 0):
                    arr = np.append(arr, right_arm_accuracy)
                    count = count + 1
                    accuracy_data['poses'].append('Right Arm')
                    accuracy_data['values'].append(right_arm_accuracy)

                # Left arm - set draw=False
                LeftArmAngle = int(detector.findAngle(frame, 11, 13, 15, draw=False))
                left_arm_accuracy = compare_left_arm(LeftArmAngle)
                if (count <= 16 and left_arm_accuracy != 0):
                    arr = np.append(arr, left_arm_accuracy)
                    count = count + 1
                    accuracy_data['poses'].append('Left Arm')
                    accuracy_data['values'].append(left_arm_accuracy)
                
                # Right leg - set draw=False
                RightLegAngle = int(detector.findAngle(frame, 24, 26, 28, draw=False))
                right_leg_accuracy = compare_right_leg(RightLegAngle)
                if (count <= 16 and right_leg_accuracy != 0):
                    arr = np.append(arr, right_leg_accuracy)
                    count = count + 1
                    accuracy_data['poses'].append('Right Leg')
                    accuracy_data['values'].append(right_leg_accuracy)
               
                # Left leg - set draw=False
                LeftLegAngle = int(detector.findAngle(frame, 23, 25, 27, draw=False))
                left_leg_accuracy = compare_left_leg(LeftLegAngle)
                if (count <= 16 and left_leg_accuracy != 0):
                    arr = np.append(arr, left_leg_accuracy)
                    count = count + 1
                    accuracy_data['poses'].append('Left Leg')
                    accuracy_data['values'].append(left_leg_accuracy)
                elif(count > 16):
                    print("entering")
                    print("accuracy: ", accuracyCalculation(arr))
                
                # Calculate overall pose accuracy for WebSocket feedback and timer
                # Filter zeros to avoid skewing the calculation
                accuracies = [a for a in [right_arm_accuracy, left_arm_accuracy, right_leg_accuracy, left_leg_accuracy] if a > 0]
                
                # Make sure we have at least one valid accuracy value
                if accuracies:
                    overall_accuracy = sum(accuracies) / len(accuracies)
                    
                    # Lower the accuracy threshold to make pose detection more lenient
                    is_correct_pose = overall_accuracy >= 70  # Lowered threshold for TensorFlow model
                    
                    # Debug output to help diagnose issues
                    if count % 30 == 0:  # Print only occasionally to avoid spamming the console
                        print(f"Accuracy: {overall_accuracy:.1f}%, Is correct: {is_correct_pose}")
                    
                    # Track pose hold time
                    current_time = time.time()
                    if is_correct_pose:
                        # First time in correct pose
                        if pose_hold_start_time is None:
                            pose_hold_start_time = current_time
                            print(f"Starting timer for correct pose: {current_pose}")
                            
                            # Increment the attempts counter when starting a new pose attempt
                            try:
                                progress_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pose_progress.json')
                                if os.path.exists(progress_data_file):
                                    with open(progress_data_file, 'r') as f:
                                        progress_data = json.load(f)
                                    
                                    if current_pose in progress_data:
                                        progress_data[current_pose]['attempts'] += 1
                                        progress_data[current_pose]['last_practiced'] = time.strftime("%Y-%m-%d %H:%M:%S")
                                        
                                        with open(progress_data_file, 'w') as f:
                                            json.dump(progress_data, f, indent=4)
                                        print(f"Incremented attempts for {current_pose}")
                            except Exception as e:
                                print(f"Error updating attempts count: {str(e)}")
                        
                        # Calculate how long they've held the correct pose
                        pose_correct_duration = current_time - pose_hold_start_time
                        
                        # Check if pose has been held long enough to be completed
                        required_time = pose_completion_times.get(current_pose, 30)  # Default 30s
                        if pose_correct_duration >= required_time and not pose_completed:
                            pose_completed = True
                            
                            # Update progress data with calculated accuracy values
                            try:
                                # Load current progress data
                                progress_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pose_progress.json')
                                if os.path.exists(progress_data_file):
                                    with open(progress_data_file, 'r') as f:
                                        progress_data = json.load(f)
                                        
                                    # Update completion count
                                    if current_pose in progress_data:
                                        progress_data[current_pose]['completions'] += 1
                                        
                                        # Update practice time
                                        progress_data[current_pose]['total_practice_time'] += pose_correct_duration
                                        
                                        # Update best accuracy if this attempt was better
                                        if overall_accuracy > progress_data[current_pose]['best_accuracy']:
                                            progress_data[current_pose]['best_accuracy'] = overall_accuracy
                                        
                                        # Update last practiced time
                                        progress_data[current_pose]['last_practiced'] = time.strftime("%Y-%m-%d %H:%M:%S")
                                        
                                        # Save the updated progress data
                                        with open(progress_data_file, 'w') as f:
                                            json.dump(progress_data, f, indent=4)
                                            
                                        print(f"Updated progress for {current_pose}: completions={progress_data[current_pose]['completions']}")
                            except Exception as e:
                                print(f"Error updating progress data: {str(e)}")
                            
                            broadcast_pose_status(is_correct_pose, pose_completed)
                            print(f"Pose completed! Held for {pose_correct_duration:.1f} seconds")
                    else:
                        # Reset hold timer if pose is incorrect (with longer grace period for TensorFlow model)
                        if pose_hold_start_time is not None and (current_time - pose_hold_start_time) > 2.0:  # Extended grace period
                            pose_hold_start_time = None
                            pose_correct_duration = 0
                            print("Pose incorrect - resetting timer")
                    
                    # Add visual feedback for pose status - don't add breathing UI here
                    h, w, c = frame.shape
                    
                    # Add overlay showing completion status when pose is completed
                    if pose_completed:
                        # Create expanded image with 100 pixels at the bottom for completion notification
                        expanded_h = h + 100
                        expanded_img = np.zeros((expanded_h, w, 3), dtype=np.uint8)
                        
                        # Copy the original image to the top portion of the expanded image
                        expanded_img[0:h, 0:w] = frame
                        
                        # Create bottom area with semi-transparent green background
                        cv2.rectangle(expanded_img, (0, h), (w, expanded_h), (0, 200, 0), -1)
                        
                        # Add text
                        font = cv2.FONT_HERSHEY_DUPLEX
                        text = "Pose Completed!"
                        text_size = cv2.getTextSize(text, font, 1.5, 2)[0]
                        text_x = (w - text_size[0]) // 2
                        text_y = h + 60
                        cv2.putText(expanded_img, text, (text_x, text_y), font, 1.5, (255, 255, 255), 2)
                        
                        frame = expanded_img
                    
                    # Add progress indicator if not completed yet but pose is correct  
                    # This is the part that shows the hold pose prompt
                    elif pose_correct_duration > 0:
                        # Calculate required time to complete pose
                        required_time = pose_completion_times.get(current_pose, 30)  # Default 30s
                        
                        # Calculate progress as a percentage
                        progress = (pose_correct_duration / required_time) * 100
                        progress = min(100, max(0, progress))  # Limit to 0-100%
                        
                        # Create expanded image with 60 pixels at the bottom for progress bar
                        expanded_h = h + 60
                        expanded_img = np.zeros((expanded_h, w, 3), dtype=np.uint8)
                        
                        # Copy the original image to the top portion of the expanded image
                        expanded_img[0:h, 0:w] = frame
                        
                        # Create bottom area with dark background
                        cv2.rectangle(expanded_img, (0, h), (w, expanded_h), (50, 50, 50), -1)
                        
                        # Background of bar
                        bar_height = 20
                        bar_y = h + 20
                        bar_width = int(w * 0.8)
                        bar_x = (w - bar_width) // 2
                        cv2.rectangle(expanded_img, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (200, 200, 200), -1)
                        
                        # Filled portion
                        filled_width = int(bar_width * (progress / 100))
                        cv2.rectangle(expanded_img, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height), (0, 255, 0), -1)
                        
                        # Text showing percentage and time remaining
                        text = f"{int(progress)}% - Hold for {int(required_time-pose_correct_duration)}s more"
                        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0]
                        text_x = (w - text_size[0]) // 2
                        text_y = h + 15
                        cv2.putText(expanded_img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA, False)
                        
                        frame = expanded_img
                    
                    # Add a small indicator in the corner even when not holding a correct pose
                    else:
                        # Add a small text indicator in the corner
                        cv2.putText(frame, "Adjust pose to match", (10, h-20), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.6, (0, 0, 255), 1, cv2.LINE_AA)
                
            cv2.waitKey(1)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield(b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            print('Original Array:', arr)
            x = range(1, len(arr) + 1)
            y = arr
            plt.plot(x, y)

def accuracyCalculation(arr):
    accArray = np.array([])
    sum = 0
    for j in range(0, len(arr) - 1, 4):
        sum = 0
        for i in range(j, min(j + 4, len(arr))):
            print("arr[i]", arr[i])
            sum = sum + arr[i]
        accur = sum / 4
        accArray = np.append(accArray, accur)
    
    return accArray

@app.route("/")
def home():
     return render_template("home.html")

@app.route('/tracks')
def tracks():
    return render_template('tracks.html')

@app.route('/yoga')
def yoga():
    return render_template('yoga.html')

@app.route('/index')
def index():
    pose = request.args.get('pose', 'vrksana')  # Default to vrksana if no pose is specified
    
    # Define pose name mappings
    pose_names = {
        'vrksana': 'Vrksasana',
        'adhomukha': 'Adho Mukha',
        'balasana': 'Balasana',
        'tadasan': 'Tadasana',
        'trikonasana': 'Trikonasana',
        'virabhadrasana': 'Virabhadrasana'
    }
    
    # Define image mappings - use exact filenames from static/images folder
    gif_mappings = {
        'vrksana': 'vrksana.jpg',
        'adhomukha': 'adho_mukha.jpeg',
        'balasana': 'balasana.jpg',
        'tadasan': 'Tad-asan.gif',  # Updated to match the actual file in static/images
        'trikonasana': 'trikonasana.jpg',
        'virabhadrasana': 'virabhadrasana.jpg',
        'bhujangasana': 'bhujangasana.jpg',
        'setubandhasana': 'setubandhasana.png',
        'uttanasana': 'uttanasana.png',
        'shavasana': 'shavasana.png',
        'ardhamatsyendrasana': 'ardhamatsyendrasana.png'
    }
    
    # Define Sanskrit names
    sanskrit_names = {
        'vrksana': 'वृक्षासन',
        'adhomukha': 'अधोमुखश्वानासन',
        'balasana': 'बालासन',
        'tadasan': 'ताड़ासन',
        'trikonasana': 'त्रिकोणासन',
        'virabhadrasana': 'वीरभद्रासन',
        'bhujangasana': 'भुजङ्गासन',
        'setubandhasana': 'सेतुबन्धासन',
        'uttanasana': 'उत्तानासन',
        'shavasana': 'शवासन',
        'ardhamatsyendrasana': 'अर्धमत्स्येन्द्रासन'
    }
    
    # Define English names
    english_names = {
        'vrksana': 'Tree Pose',
        'adhomukha': 'Downward Facing Dog',
        'balasana': 'Child\'s Pose',
        'tadasan': 'Mountain Pose',
        'trikonasana': 'Triangle Pose',
        'virabhadrasana': 'Warrior Pose',
        'bhujangasana': 'Cobra Pose',
        'setubandhasana': 'Bridge Pose',
        'uttanasana': 'Standing Forward Bend',
        'shavasana': 'Corpse Pose',
        'ardhamatsyendrasana': 'Half Lord of the Fishes Pose'
    }
    
    # Define breathing patterns
    breathing_patterns = {
        'vrksana': {'total_cycle': 6, 'inhale_ratio': 0.4},       # Tree pose: 2.4s inhale, 3.6s exhale
        'adhomukha': {'total_cycle': 8, 'inhale_ratio': 0.5},     # Downward dog: 4s inhale, 4s exhale 
        'balasana': {'total_cycle': 10, 'inhale_ratio': 0.3},     # Child's pose: 3s inhale, 7s exhale (more relaxed)
        'tadasan': {'total_cycle': 5, 'inhale_ratio': 0.5},       # Mountain pose: 2.5s inhale, 2.5s exhale
        'trikonasana': {'total_cycle': 7, 'inhale_ratio': 0.4},   # Triangle pose: 2.8s inhale, 4.2s exhale
        'virabhadrasana': {'total_cycle': 6, 'inhale_ratio': 0.45} # Warrior pose: 2.7s inhale, 3.3s exhale
    }
    
    # Get the current pattern
    pattern = breathing_patterns.get(pose, breathing_patterns['vrksana'])
    
    # Calculate breathing times
    inhale_time = round(pattern['total_cycle'] * pattern['inhale_ratio'], 1)
    exhale_time = round(pattern['total_cycle'] * (1 - pattern['inhale_ratio']), 1)
    
    # Get the proper pose name and image file
    pose_name = pose_names.get(pose, 'Vrksasana')
    gif_name = gif_mappings.get(pose, 'vrksana.jpg')
    sanskrit_name = sanskrit_names.get(pose, '')
    english_name = english_names.get(pose, '')
    
    # Store the selected pose in global variable
    global current_pose, pose_hold_start_time, pose_correct_duration, pose_completed
    current_pose = pose
    
    # Reset pose tracking when pose changes
    pose_hold_start_time = None
    pose_correct_duration = 0
    pose_completed = False
    
    # Also update the detector's pose name
    global detector
    detector.setPose(pose)
    
    return render_template('index.html', 
                          pose_name=pose_name, 
                          gif_name=gif_name,
                          pose_param=pose,
                          sanskrit_name=sanskrit_name,
                          english_name=english_name,
                          pattern=pattern,
                          inhale_time=inhale_time,
                          exhale_time=exhale_time)

@app.route('/charts')
def charts():
    # Use the updated accuracy data
    if len(accuracy_data['values']) == 0:
        # Generate sample data if no real data exists yet
        values = [67, 78, 68, 89, 69, 59, 70, 61, 84, 78]
    else:
        values = accuracy_data['values']
        
    labels = ['Right Arm', 'Left Arm', 'Right Leg', 'Left Leg']
    colors = ['#ff0000','#0000ff','#ffffe0','#008000','#800080','#FFA500', '#FF2554']
    
    # Initialize progress data tracking if not already present
    progress_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pose_progress.json')
    
    # Create progress data file if it doesn't exist
    if not os.path.exists(progress_data_file):
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
        
        # Save initial progress data
        try:
            with open(progress_data_file, 'w') as f:
                json.dump(data, f, indent=4)
            print("Initial progress data file created")
        except Exception as e:
            print(f"Error creating progress data file: {str(e)}")
    
    return render_template('charts.html', values=values, labels=labels, colors=colors)

@app.route('/video')
def video():
    # Get the pose parameter from the request
    pose = request.args.get('pose', 'vrksana')
    
    # Update global detector with the selected pose
    global detector, pose_hold_start_time, pose_correct_duration, pose_completed
    detector.setPose(pose)
    
    # Reset pose tracking
    pose_hold_start_time = None
    pose_correct_duration = 0
    pose_completed = False
    
    return Response(generate_frames(arr), mimetype='multipart/x-mixed-replace; boundary=frame')

# API endpoints for React frontend
@app.route('/api/poses', methods=['GET'])
def get_poses():
    """Return all available poses"""
    poses = [
        {
            "id": "vrksana",
            "name": "Vrksasana",
            "sanskritName": "वृक्षासन",
            "englishName": "Tree Pose",
            "description": "A classic standing posture. It establishes strength and balance, and helps you feel centered.",
            "benefits": [
                "Improves balance and stability",
                "Strengthens the legs, ankles, and feet",
                "Opens the hips and stretches the inner thighs",
                "Improves focus and concentration",
                "Builds confidence and self-esteem"
            ],
            "instructions": [
                "Begin standing with feet together, arms at sides.",
                "Shift weight to left foot, bending right knee.",
                "Place right foot on left inner thigh, toes pointing down.",
                "Bring palms together at heart center or reach arms overhead.",
                "Fix gaze on a steady point for balance.",
                "Hold for 30-60 seconds, then switch sides."
            ],
            "cautions": [
                "Avoid if you have low blood pressure or migraine",
                "Be cautious if you have knee, hip, or ankle injuries",
                "Use a wall for support if balance is challenging"
            ],
            "imageSrc": "/static/images/vrksana.jpg",
            "gifName": "vrksana.jpg"
        },
        {
            "id": "adhomukha",
            "name": "Adho Mukha",
            "sanskritName": "अधोमुखश्वानासन",
            "englishName": "Downward Facing Dog",
            "description": "It strengthens the core and improves circulation, while providing full-body stretch.",
            "benefits": [
                "Stretches the hamstrings, calves, and shoulders",
                "Strengthens the arms, shoulders, and legs",
                "Increases blood flow to the brain",
                "Relieves back pain and tension",
                "Energizes the body"
            ],
            "instructions": [
                "Start on hands and knees, hands shoulder-width apart.",
                "Tuck toes and lift knees off the floor.",
                "Straighten legs as much as possible, lifting hips toward ceiling.",
                "Press chest toward thighs, creating an inverted V-shape.",
                "Keep head between arms, gazing toward navel.",
                "Hold for 1-3 minutes, breathing deeply."
            ],
            "cautions": [
                "Modify if you have carpal tunnel syndrome",
                "Bend knees if hamstrings are tight",
                "Not recommended for those with severe hypertension"
            ],
            "imageSrc": "/static/images/adho_mukha.jpeg",
            "gifName": "adho_mukha.jpeg"
        },
        {
            "id": "balasana",
            "name": "Balasana",
            "sanskritName": "बालासन",
            "englishName": "Child's Pose",
            "description": "Balasana is a restful pose that can be sequenced between more challenging asanas.",
            "benefits": [
                "Gently stretches the lower back and hips",
                "Relieves stress and fatigue",
                "Calms the mind and reduces anxiety",
                "Helps release tension in the shoulders",
                "Promotes relaxation and surrender"
            ],
            "instructions": [
                "Kneel on the floor with knees hip-width apart.",
                "Touch big toes together and sit on heels.",
                "Exhale and lay torso down between thighs.",
                "Extend arms forward or alongside body.",
                "Rest forehead on mat and breathe deeply.",
                "Hold for 30 seconds to several minutes."
            ],
            "cautions": [
                "Use caution with knee injuries",
                "Avoid during late pregnancy",
                "Modify with props if needed for comfort"
            ],
            "imageSrc": "/static/images/balasana.jpg",
            "gifName": "balasana.jpg"
        },
        {
            "id": "tadasan",
            "name": "Tadasan",
            "sanskritName": "ताड़ासन",
            "englishName": "Mountain Pose",
            "description": "The foundation of all standing poses. It improves posture, balance, and body awareness.",
            "benefits": [
                "Improves posture and alignment",
                "Strengthens thighs, knees, and ankles",
                "Increases awareness and focus",
                "Develops steady breathing",
                "Creates a foundation for other standing poses"
            ],
            "instructions": [
                "Stand with feet together or hip-width apart.",
                "Distribute weight evenly through feet.",
                "Engage thigh muscles and lift kneecaps.",
                "Lengthen spine and lift chest.",
                "Relax shoulders down and back.",
                "Breathe deeply for 30-60 seconds."
            ],
            "cautions": [
                "Widen stance if balance is difficult",
                "Use a wall for support if needed",
                "Modify if you have low blood pressure"
            ],
            "imageSrc": "/static/images/Tad-asan.gif",
            "gifName": "Tad-asan.gif"
        },
        {
            "id": "trikonasana",
            "name": "Trikonasana",
            "sanskritName": "त्रिकोणासन",
            "englishName": "Triangle Pose",
            "description": "It is a quintessential standing pose that stretches and strengthens the whole body.",
            "benefits": [
                "Stretches legs, hips, groin, and hamstrings",
                "Strengthens thighs, knees, and ankles",
                "Opens chest and shoulders",
                "Improves digestion",
                "Reduces stress and anxiety"
            ],
            "instructions": [
                "Stand with feet wide apart.",
                "Turn right foot out 90° and left foot slightly in.",
                "Extend arms parallel to floor.",
                "Reach right hand down toward right ankle.",
                "Extend left arm toward ceiling.",
                "Hold for 30-60 seconds, then switch sides."
            ],
            "cautions": [
                "Avoid if you have severe back pain",
                "Use a block under hand if flexibility is limited",
                "Modify head position if you have neck issues"
            ],
            "imageSrc": "/static/images/trikonasana.jpg",
            "gifName": "trikonasana.jpg"
        },
        {
            "id": "virabhadrasana",
            "name": "Virabhadrasana",
            "sanskritName": "वीरभद्रासन",
            "englishName": "Warrior Pose",
            "description": "It is a foundational yoga pose that balances flexibility and strength in true warrior fashion.",
            "benefits": [
                "Strengthens legs, core, and back",
                "Opens hips and chest",
                "Improves concentration and balance",
                "Builds stamina and endurance",
                "Stimulates abdominal organs"
            ],
            "instructions": [
                "Start in Mountain Pose, step one foot back.",
                "Align front heel with back arch.",
                "Bend front knee over ankle.",
                "Lift arms overhead or alongside body.",
                "Gaze forward and breathe steadily.",
                "Hold for 30-60 seconds, then switch sides."
            ],
            "cautions": [
                "Avoid with high blood pressure (arms overhead)",
                "Modify knee bend if you have knee issues",
                "Use caution with shoulder injuries"
            ],
            "imageSrc": "/static/images/virabhadrasana.jpg",
            "gifName": "virabhadrasana.jpg"
        }
    ]
    return jsonify(poses)

@app.route('/api/poses/<pose_id>', methods=['GET'])
def get_pose(pose_id):
    """Return details for a specific pose"""
    poses = json.loads(get_poses().get_data())
    pose = next((p for p in poses if p["id"] == pose_id), None)
    
    if pose:
        return jsonify(pose)
    else:
        return jsonify({"error": "Pose not found"}), 404

@app.route('/api/accuracy', methods=['GET'])
def get_accuracy():
    """Return accuracy data for analytics"""
    if len(accuracy_data['values']) == 0:
        values = [67, 78, 68, 89, 69, 59, 70, 61, 84, 78]
    else:
        values = accuracy_data['values']
    
    labels = ['Right Arm', 'Left Arm', 'Right Leg', 'Left Leg']
    return jsonify({
        'values': values,
        'labels': labels,
        'poses': accuracy_data.get('poses', ['Pose 1', 'Pose 2', 'Pose 3', 'Pose 4'])
    })

@app.route('/api/video')
def api_video():
    """API endpoint for video stream"""
    pose = request.args.get('pose', 'vrksana')
    global detector, pose_hold_start_time, pose_correct_duration, pose_completed
    detector.setPose(pose)
    
    # Reset pose tracking
    pose_hold_start_time = None
    pose_correct_duration = 0
    pose_completed = False
    
    return Response(generate_frames(arr), mimetype='multipart/x-mixed-replace; boundary=frame')

# WebSocket route
@app.route('/ws/pose_feedback')
def pose_feedback_ws():
    """WebSocket endpoint for pose feedback"""
    return "WebSocket endpoint for pose feedback. Connect with a WebSocket client."

# Serve static images with fallback to placeholder
@app.route('/static/images/<path:filename>')
def serve_static_images(filename):
    """Try to serve static images with fallback to placeholder"""
    # First check if the file exists in the static folder
    file_path = os.path.join(os.path.dirname(__file__), 'static', 'images', filename)
    
    if os.path.isfile(file_path):
        # If file exists, serve it directly from the actual static folder
        return app.send_static_file(f'images/{filename}')
    else:
        # If not found, extract the pose name from the filename and return a 404
        print(f"Image not found: {filename}")
        return "Image not found", 404

def start_websocket_background():
    """Start WebSocket server in a background thread"""
    # Start the WebSocket server in a daemon thread
    # The actual asyncio loop initialization is now handled within start_websocket_server
    websocket_thread = threading.Thread(target=start_websocket_server, daemon=True)
    websocket_thread.name = "WebSocketThread"  # Name the thread for easier debugging
    websocket_thread.start()
    print("WebSocket server thread started")
    
    # Give the thread a moment to initialize
    time.sleep(0.5)

if __name__ == "__main__":
    print(f"Static folder path: {app.static_folder}")
    
    # Start WebSocket server in the background
    start_websocket_background()
    
    # Start the Flask app
    app.run(host="127.0.0.1", debug=True)