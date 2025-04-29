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

# Define the app with the path to the React build directory
app = Flask(__name__, 
    static_folder='ui-wizard-enhancements/dist',
    static_url_path='/'
)

# Enable CORS for development
CORS(app)
app.secret_key = 'yoga_app_secret_key'

def initialize_hf_model():
    """Initialize the HuggingFace model"""
    global hf_classifier
    
    if hf_classifier is None:
        print("Initializing HuggingFace model... (first request only)")
        try:
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
        
        # Set default resolution to 480p
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
            # For visualization purposes, we'll create 4 simulated body parts with similar values
            accuracy_value = int(confidence * 100) if is_correct else int(confidence * 50)
            
            # Ensure accuracy is not too low even when correct pose is detected
            if is_correct and accuracy_value < 70:
                accuracy_value = 70 + int(confidence * 30)
            
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
        
        # Add a breathing guide indicator
        breathing_cycle = 6  # seconds
        breathing_phase = (time.time() % breathing_cycle) / breathing_cycle
        is_inhale = breathing_phase < 0.4  # 40% inhale, 60% exhale
        
        breath_text = "INHALE" if is_inhale else "EXHALE"
        breath_color = (0, 255, 0) if is_inhale else (0, 0, 255)
        
        cv2.putText(frame, breath_text, (frame.shape[1] - 120, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, breath_color, 2)
                
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
    global current_pose
    current_pose = pose
    
    # Return the video stream
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

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
            "name": "Tadasana",
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
        },
        {
            "id": "bhujangasana",
            "name": "Bhujangasana",
            "sanskritName": "भुजङ्गासन",
            "englishName": "Cobra Pose",
            "description": "A gentle backbend that strengthens the spine and opens the chest.",
            "benefits": [
                "Strengthens the spine and back muscles",
                "Opens chest and shoulders",
                "Improves posture and counteracts slouching",
                "Stimulates abdominal organs",
                "Increases flexibility of the spine"
            ],
            "instructions": [
                "Lie on your stomach with legs extended behind you.",
                "Place palms under shoulders, elbows close to your body.",
                "Press into hands and lift chest off the floor.",
                "Keep lower ribs on the floor and look forward.",
                "Maintain space between shoulders and ears.",
                "Hold for 15-30 seconds, breathing deeply."
            ],
            "cautions": [
                "Avoid with severe back problems or hernia",
                "Practice with caution if you have neck injuries",
                "Not recommended during pregnancy"
            ],
            "imageSrc": "/static/images/bhujangasana.jpg",
            "gifName": "bhujangasana.jpg"
        },
        {
            "id": "setubandhasana",
            "name": "Setu Bandhasana",
            "sanskritName": "सेतुबन्धासन",
            "englishName": "Bridge Pose",
            "description": "A gentle backbend that strengthens the back and opens the chest.",
            "benefits": [
                "Strengthens the back, glutes, and hamstrings",
                "Opens the chest and shoulders",
                "Improves circulation and digestion",
                "Reduces anxiety and stress",
                "Relieves mild backache and fatigue"
            ],
            "instructions": [
                "Lie on your back with knees bent, feet flat on the floor.",
                "Place feet hip-width apart, close to your buttocks.",
                "Press into your feet and lift hips toward ceiling.",
                "Clasp hands beneath your back or keep arms alongside body.",
                "Keep thighs and feet parallel.",
                "Hold for 30-60 seconds, then gently lower down."
            ],
            "cautions": [
                "Avoid with neck injuries or severe back pain",
                "Use caution if you have high blood pressure",
                "Support with a block under sacrum if needed"
            ],
            "imageSrc": "/static/images/setubandhasana.png",
            "gifName": "setubandhasana.png"
        },
        {
            "id": "uttanasana",
            "name": "Uttanasana",
            "sanskritName": "उत्तानासन",
            "englishName": "Standing Forward Bend",
            "description": "A calming forward fold that stretches the entire back of the body.",
            "benefits": [
                "Stretches hamstrings, calves, and hips",
                "Strengthens thighs and knees",
                "Reduces stress, anxiety, and fatigue",
                "Relieves headache and insomnia",
                "Stimulates liver and kidneys"
            ],
            "instructions": [
                "Begin standing with feet hip-width apart.",
                "Exhale and bend forward from the hip joints.",
                "Lengthen the front of your torso as you fold.",
                "Place hands on the floor or hold onto your ankles.",
                "Allow your head to hang freely.",
                "Hold for 30-60 seconds, breathing deeply."
            ],
            "cautions": [
                "Avoid with back injuries or sciatica",
                "Bend knees if hamstrings are tight",
                "Use caution with high blood pressure or headache"
            ],
            "imageSrc": "/static/images/uttanasana.png",
            "gifName": "uttanasana.png"
        },
        {
            "id": "shavasana",
            "name": "Shavasana",
            "sanskritName": "शवासन",
            "englishName": "Corpse Pose",
            "description": "A restorative pose that relaxes the entire body and calms the mind.",
            "benefits": [
                "Deeply relaxes the entire body",
                "Reduces blood pressure and anxiety",
                "Improves concentration and mental clarity",
                "Helps manage insomnia and fatigue",
                "Promotes mindfulness and meditation"
            ],
            "instructions": [
                "Lie flat on your back on a comfortable surface.",
                "Extend legs and allow feet to fall out to the sides.",
                "Rest arms alongside body, palms facing upward.",
                "Close your eyes and relax your entire body.",
                "Focus on your natural breath without controlling it.",
                "Remain in the pose for 5-10 minutes."
            ],
            "cautions": [
                "Support lower back with a pillow if needed",
                "Use a folded blanket under head for neck comfort",
                "May be uncomfortable for those with respiratory issues"
            ],
            "imageSrc": "/static/images/shavasana.png",
            "gifName": "shavasana.png"
        },
        {
            "id": "ardhamatsyendrasana",
            "name": "Ardha Matsyendrasana",
            "sanskritName": "अर्धमत्स्येन्द्रासन",
            "englishName": "Half Lord of the Fishes Pose",
            "description": "A seated twist that improves spine mobility and stimulates digestion.",
            "benefits": [
                "Improves spine mobility and flexibility",
                "Stimulates digestive organs",
                "Relieves lower backache and hip pain",
                "Strengthens and stretches the shoulders",
                "Improves energy levels and mental focus"
            ],
            "instructions": [
                "Sit with legs extended in front of you.",
                "Bend right knee and place foot outside left thigh.",
                "Bend left knee and tuck left foot near right buttock.",
                "Twist torso to the right, placing left elbow outside right knee.",
                "Look over right shoulder, keeping spine tall.",
                "Hold for 30-60 seconds, then repeat on other side."
            ],
            "cautions": [
                "Avoid with severe back or spinal issues",
                "Modify if you have knee problems",
                "Practice with caution during pregnancy"
            ],
            "imageSrc": "/static/images/ardhamatsyendrasana.png",
            "gifName": "ardhamatsyendrasana.png"
        }
    ]
    return jsonify(poses)

@app.route('/api/poses/<pose_id>', methods=['GET'])
def get_pose(pose_id):
    """Return details for a specific pose"""
    # This would normally come from a database
    poses = json.loads(get_poses().get_data())
    pose = next((p for p in poses if p["id"] == pose_id), None)
    
    if pose:
        return jsonify(pose)
    else:
        return jsonify({"error": "Pose not found"}), 404

@app.route('/api/accuracy', methods=['GET'])
def get_accuracy():
    """Return accuracy data for analytics"""
    # Use the existing accuracy_data
    if len(accuracy_data['values']) == 0:
        values = [67, 78, 68, 89]
    else:
        values = accuracy_data['values']
    
    labels = ['Right Arm', 'Left Arm', 'Right Leg', 'Left Leg']
    return jsonify({
        'values': values,
        'labels': labels,
        'poses': accuracy_data.get('poses', [current_pose] * 4)
    })

@app.route('/api/video')
def api_video():
    """API endpoint for video stream"""
    # Identical to /video endpoint
    return video()

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

if __name__=="__main__":
    print("Starting HuggingFace-only Yoga Pose Detection server...")
    print("This version uses ONLY the HuggingFace model (no TensorFlow or MediaPipe)")
    print("Flask application ready. HuggingFace model will load when first needed.")
    app.run(host="127.0.0.1", port=5000, debug=True)