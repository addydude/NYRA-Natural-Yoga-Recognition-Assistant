import torch
from transformers import AutoModelForImageClassification
import PIL.Image as Image
import os
import numpy as np
import cv2
import logging
import traceback

class HuggingFacePoseClassifier:
    def __init__(self, model_name="AdityasArsenal/finetuned-for-YogaPosesv6"):
        """
        Initialize the Hugging Face yoga pose classifier with custom preprocessing.
        
        Args:
            model_name (str): The name of the Hugging Face model to use.
        """
        print(f"Loading Hugging Face model: {model_name}")
        self.model_name = model_name
        
        # Load model with standard image preprocessing approach
        try:
            # Try to load the model
            self.model = AutoModelForImageClassification.from_pretrained(model_name)
            
            # Set model to evaluation mode
            self.model.eval()
            
            print(f"Model loaded successfully with {len(self.model.config.id2label)} yoga pose classes")
            self.id2label = self.model.config.id2label
            
            # Print the available classes with their indices for debugging
            print("Available class mappings:")
            for idx, label in self.id2label.items():
                print(f"  {idx}: {label}")
            
            # Create a reverse mapping for fallback purposes
            self._create_fallback_mappings()
            
            # Create custom pose mappings for our specific application
            self._create_pose_mappings()
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            traceback.print_exc()
            raise
    
    def _create_fallback_mappings(self):
        """Create fallback mappings in case we encounter unknown class indices"""
        # Store numerical keys for easy integer-based lookup
        self.numeric_keys = []
        for key in self.id2label.keys():
            try:
                self.numeric_keys.append(int(key))
            except:
                pass  # Skip non-numeric keys
        
        # Sort for consistent fallback behavior
        self.numeric_keys.sort()
        
        # Store default fallback class
        if len(self.id2label) > 0:
            self.fallback_class = next(iter(self.id2label.values()))
            # Also store the first key as the default key
            self.default_key = next(iter(self.id2label.keys()))
        else:
            self.fallback_class = "unknown"
            self.default_key = "0"
        
        # Print available keys for debugging
        print(f"Available ID keys: {list(self.id2label.keys())}")
    
    def _create_pose_mappings(self):
        """Create custom mappings between model output classes and our application's pose names"""
        # Map from model's class indices to our application's pose names
        self.class_to_pose_map = {
            # Numeric keys common in HF models
            0: 'vrksana',  # Tree pose
            1: 'balasana', # Child's pose
            2: 'trikonasana', # Triangle pose
            3: 'virabhadrasana', # Warrior pose
            4: 'adhomukha', # Downward dog
            5: 'tadasan',  # Mountain pose
            6: 'bhujangasana', # Cobra pose
            7: 'setubandhasana', # Bridge pose
            8: 'uttanasana', # Standing forward bend
            9: 'shavasana', # Corpse pose
            10: 'ardhamatsyendrasana', # Half lord of the fishes
            
            # String mappings for common pose names
            'Tree': 'vrksana',
            'Tree Pose': 'vrksana',
            'Child': 'balasana',
            'Child Pose': 'balasana',
            'Childs_pose': 'balasana',
            'Chair': 'balasana',  # Also mapping Chair to balasana (similar in app)
            'Triangle': 'trikonasana',
            'Triangle Pose': 'trikonasana',
            'Warrior': 'virabhadrasana',
            'Warrior1': 'virabhadrasana',
            'Warrior2': 'virabhadrasana',
            'Warrior Pose': 'virabhadrasana',
            'Downdog': 'adhomukha',
            'Downward Dog': 'adhomukha',
            'Down_dog': 'adhomukha',
            'Downward_dog': 'adhomukha',
            'Downward_facing_dog': 'adhomukha',
            'Mountain': 'tadasan',
            'Mountain_pose': 'tadasan',
            'Cobra': 'bhujangasana',
            'Cobra_pose': 'bhujangasana',
            'Bridge': 'setubandhasana',
            'Bridge_pose': 'setubandhasana',
            'StandingForwardBend': 'uttanasana',
            'Standing_forward_bend': 'uttanasana',
            'Forward_bend': 'uttanasana',
            'Corpse': 'shavasana',
            'Corpse_pose': 'shavasana',
            'Twists': 'ardhamatsyendrasana',
            'Fish': 'ardhamatsyendrasana',
            'Half_lord_of_fishes': 'ardhamatsyendrasana',
            'Goddess': 'trikonasana',  # Mapping Goddess to triangle as in the app
            'Plank': 'balasana'  # Mapping Plank to balasana as in the app
        }
        
        # Also add lowercase versions for case-insensitive matching
        lowercase_mappings = {}
        for class_name, pose_name in list(self.class_to_pose_map.items()):
            if isinstance(class_name, str):
                lowercase_mappings[class_name.lower()] = pose_name
        
        # Update the map with lowercase entries
        self.class_to_pose_map.update(lowercase_mappings)
        
        # Create the reverse mapping for validation purposes
        self.pose_to_class_map = {}
        for class_idx, pose_name in self.class_to_pose_map.items():
            if isinstance(class_idx, int):  # Only map numeric indices
                self.pose_to_class_map[pose_name] = class_idx
                
        print(f"Created mappings for {len(self.pose_to_class_map)} poses")
        
        # For debug purposes, print a few mappings
        print("Sample pose mappings:")
        sample_keys = list(self.class_to_pose_map.keys())[:5]
        for key in sample_keys:
            print(f"  {key} -> {self.class_to_pose_map[key]}")
        
    def map_to_pose_name(self, class_index_or_name):
        """Convert model's output class to our application's pose name"""
        # First try numeric mapping
        if isinstance(class_index_or_name, int) and class_index_or_name in self.class_to_pose_map:
            return self.class_to_pose_map[class_index_or_name]
            
        # If it's a string, try string mapping after converting to lowercase
        if isinstance(class_index_or_name, str):
            lower_name = class_index_or_name.lower()
            if lower_name in self.class_to_pose_map:
                return self.class_to_pose_map[lower_name]
                
        # Return the original input if no mapping found
        return class_index_or_name
    
    def preprocess_image(self, image):
        """
        Custom preprocessing function for yoga pose images.
        Works without requiring preprocessor_config.json
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            preprocessed tensor ready for model
        """
        # Convert numpy array to PIL Image if needed
        if isinstance(image, np.ndarray):
            # If BGR (OpenCV), convert to RGB
            if image.shape[-1] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            
        # Resize to standard size for most vision models (224x224)
        image = image.resize((224, 224))
        
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        # Convert to numpy array
        img_array = np.array(image)
        
        # Normalize to [0, 1]
        img_array = img_array.astype(np.float32) / 255.0
        
        # Normalize with ImageNet mean and std
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img_array = (img_array - mean) / std
        
        # Convert to tensor format [1, 3, 224, 224]
        img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0).float()
        
        return img_tensor
        
    def predict(self, image_path):
        """
        Predict the yoga pose from an image path.
        
        Args:
            image_path (str): Path to the image file.
            
        Returns:
            dict: A dictionary containing the predicted pose and confidence.
        """
        if not os.path.exists(image_path):
            return {"error": f"Image not found at {image_path}"}
        
        try:
            # Load and preprocess the image
            image = Image.open(image_path).convert("RGB")
            
            # Preprocess using our custom function
            inputs = self.preprocess_image(image)
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(inputs)
                
            # Get predicted class
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=1)
            
            # Get top prediction
            predicted_class_idx = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class_idx].item()
            
            # Get class name with better error handling
            predicted_class = self._safe_get_class_label(predicted_class_idx)
            
            # Map to our application's pose name
            predicted_pose = self.map_to_pose_name(predicted_class_idx) or predicted_class
            
            return {
                "pose": predicted_pose,
                "original_class": predicted_class,
                "confidence": confidence * 100  # Convert to percentage
            }
            
        except Exception as e:
            return {"error": f"Prediction error: {str(e)}"}
    
    def _safe_get_class_label(self, class_idx):
        """Safely get a class label with fallback options if the index isn't found"""
        try:
            # First try direct lookup
            predicted_class_str = str(class_idx)
            if predicted_class_str in self.id2label:
                return self.id2label[predicted_class_str]
            
            # If that fails, try to find the closest numerical index
            if self.numeric_keys:
                try:
                    # Find closest available class index
                    closest_idx = min(self.numeric_keys, key=lambda x: abs(x - class_idx))
                    closest_key = str(closest_idx)
                    if closest_key in self.id2label:
                        print(f"Using closest class index: {closest_key} instead of {class_idx}")
                        return self.id2label[closest_key]
                except Exception as e:
                    print(f"Error finding closest class index: {str(e)}")
            
            # Check if we have a custom mapping for this class index
            if class_idx in self.class_to_pose_map:
                pose_name = self.class_to_pose_map[class_idx]
                print(f"Using custom mapping for class index {class_idx} -> {pose_name}")
                return pose_name
                    
            # Last resort fallback - use the first class in the dictionary
            print(f"Using fallback class '{self.fallback_class}' for unknown class index {class_idx}")
            return self.fallback_class
            
        except Exception as e:
            print(f"Error in _safe_get_class_label: {str(e)}")
            print(f"Available labels: {self.id2label}")
            # Ultimate fallback - if all else fails, return "unknown"
            return "unknown"
    
    def classify_image(self, img):
        """
        Classify a yoga pose from a numpy array (OpenCV frame) or PIL image.
        Args:
            img: numpy array (BGR or RGB) or PIL.Image.Image
        Returns:
            pose_name: Predicted pose label, mapped to our application's pose names
            confidence: Confidence score (0-1)
        """
        try:
            # Preprocess using our custom function
            inputs = self.preprocess_image(img)
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(inputs)
            
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=1)
            predicted_class_idx = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class_idx].item()
            
            # First get the standard class label
            predicted_class = self._safe_get_class_label(predicted_class_idx)
            
            # Then map to our application's pose name
            predicted_pose = self.map_to_pose_name(predicted_class_idx)
            
            # If mapping didn't work, use the original class
            if not predicted_pose or predicted_pose == predicted_class_idx:
                predicted_pose = predicted_class
                
            print(f"Classified as: {predicted_pose} (original class: {predicted_class}) with {confidence*100:.2f}% confidence")
                
            return predicted_pose, confidence
            
        except Exception as e:
            print(f"Error during classification: {str(e)}")
            traceback.print_exc()
            return "unknown", 0.0

    def get_available_classes(self):
        """
        Get all available yoga pose classes from the model.
        
        Returns:
            list: List of class names.
        """
        return list(self.id2label.values())


# Example usage
if __name__ == "__main__":
    classifier = HuggingFacePoseClassifier()
    # Use an existing image from the assets folder
    test_image = "assets/photo1.png"  # Change this to your test image
    
    # Check if file exists, if not try another image
    if not os.path.exists(test_image):
        test_image = "static/images/balasana.jpg"
        if not os.path.exists(test_image):
            test_image = next((os.path.join("assets", f) for f in os.listdir("assets") 
                              if f.endswith((".jpg", ".jpeg", ".png"))), None)
            if not test_image:
                print(f"No test images found. Please provide a valid image path.")
                import sys
                sys.exit(1)
    
    print(f"Testing with image: {test_image}")
    result = classifier.predict(test_image)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Predicted pose: {result['pose']} with {result['confidence']:.2f}% confidence")
        if 'original_class' in result and result['original_class'] != result['pose']:
            print(f"Original class from model: {result['original_class']}")