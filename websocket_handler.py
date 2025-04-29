import json
import asyncio
import websockets
import os
import time
from typing import Dict, Set, Any

# Store active connections
active_connections: Set[websockets.WebSocketServerProtocol] = set()
# Store pose data for each connection
pose_data: Dict[websockets.WebSocketServerProtocol, Dict[str, Any]] = {}

# Path to progress data file
progress_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pose_progress.json')

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
        # Create the initial progress data file if it doesn't exist
        data = initialize_progress_data()
        save_progress_data(data)
        return data
            
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
        print(f"Progress data saved successfully to {progress_data_file}")
    except Exception as e:
        print(f"Error saving progress data: {str(e)}")

async def handle_websocket(websocket, path):
    """Handle WebSocket connections for pose feedback"""
    try:
        # Add connection to active connections
        active_connections.add(websocket)
        pose_data[websocket] = {
            "pose": "vrksana", 
            "is_correct_pose": False, 
            "pose_completed": False,
            "practice_start_time": time.time()
        }
        
        # Load progress data when connection starts
        progress_data = load_progress_data()
        
        # Keep connection open and handle messages
        async for message in websocket:
            try:
                data = json.loads(message)
                
                # If client sets a pose
                if "pose" in data:
                    old_pose = pose_data[websocket]["pose"]
                    new_pose = data["pose"]
                    pose_data[websocket]["pose"] = new_pose
                    print(f"Client set pose: {new_pose}")
                    
                    # Record practice time for previous pose if changing poses
                    if old_pose != new_pose and "practice_start_time" in pose_data[websocket]:
                        practice_duration = time.time() - pose_data[websocket]["practice_start_time"]
                        if practice_duration >= 5 and old_pose in progress_data:
                            progress_data[old_pose]["total_practice_time"] += practice_duration
                            progress_data[old_pose]["last_practiced"] = time.strftime("%Y-%m-%d %H:%M:%S")
                            save_progress_data(progress_data)
                    
                    # Reset practice timer for new pose
                    pose_data[websocket]["practice_start_time"] = time.time()
                    
                    # Increment attempt count for the new pose
                    if new_pose in progress_data:
                        progress_data[new_pose]["attempts"] += 1
                        progress_data[new_pose]["last_practiced"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        save_progress_data(progress_data)
                
                # If backend sends pose status update
                if "is_correct_pose" in data:
                    pose_data[websocket]["is_correct_pose"] = data["is_correct_pose"]
                    
                    # Send the updated information back to client
                    await websocket.send(json.dumps({
                        "is_correct_pose": pose_data[websocket]["is_correct_pose"]
                    }))
                
                # If backend sends pose completion update  
                if "pose_completed" in data:
                    pose_data[websocket]["pose_completed"] = data["pose_completed"]
                    current_pose = pose_data[websocket]["pose"]
                    
                    # Update completion statistics when pose is completed
                    if data["pose_completed"] and current_pose in progress_data:
                        progress_data[current_pose]["completions"] += 1
                        
                        # Update accuracy if provided
                        if "accuracy" in data:
                            accuracy = data["accuracy"]
                            if accuracy > progress_data[current_pose]["best_accuracy"]:
                                progress_data[current_pose]["best_accuracy"] = accuracy
                        
                        # Save updated progress data
                        save_progress_data(progress_data)
                    
                    # Send the completion notification to client
                    if data["pose_completed"]:
                        await websocket.send(json.dumps({
                            "pose_completed": True
                        }))
            except json.JSONDecodeError:
                print(f"Invalid JSON received: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
    finally:
        # Clean up when connection closes
        active_connections.remove(websocket)
        
        # Record practice time for the last pose when disconnecting
        if websocket in pose_data:
            current_pose = pose_data[websocket]["pose"]
            if "practice_start_time" in pose_data[websocket]:
                practice_duration = time.time() - pose_data[websocket]["practice_start_time"]
                
                # Only record if they practiced for at least 5 seconds
                progress_data = load_progress_data()
                if practice_duration >= 5 and current_pose in progress_data:
                    progress_data[current_pose]["total_practice_time"] += practice_duration
                    save_progress_data(progress_data)
                    print(f"Recorded {practice_duration:.1f}s practice time for {current_pose} on disconnect")
            
            del pose_data[websocket]

async def send_pose_status(websocket, is_correct_pose, pose_completed=False):
    """Send pose status update to specific client"""
    if websocket in active_connections:
        try:
            await websocket.send(json.dumps({
                "is_correct_pose": is_correct_pose,
                "pose_completed": pose_completed
            }))
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed while sending status")
            active_connections.remove(websocket)
            if websocket in pose_data:
                del pose_data[websocket]

async def broadcast_pose_status(is_correct_pose, pose_completed=False):
    """Send pose status update to all connected clients"""
    disconnected = set()
    
    for websocket in active_connections:
        try:
            await websocket.send(json.dumps({
                "is_correct_pose": is_correct_pose,
                "pose_completed": pose_completed
            }))
        except websockets.exceptions.ConnectionClosed:
            disconnected.add(websocket)
    
    # Clean up disconnected clients
    for websocket in disconnected:
        active_connections.remove(websocket)
        if websocket in pose_data:
            del pose_data[websocket]

def start_websocket_server(host='0.0.0.0', port=8765):
    """Start WebSocket server"""
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Create the server coroutine
    start_server = websockets.serve(handle_websocket, host, port)
    print(f"WebSocket server starting on {host}:{port}")
    
    try:
        # Schedule the server to run in the loop
        loop.run_until_complete(start_server)
        # Run the loop forever
        loop.run_forever()
    except KeyboardInterrupt:
        print("WebSocket server stopped")
    finally:
        # Close the loop properly when done
        loop.close()

if __name__ == "__main__":
    start_websocket_server()