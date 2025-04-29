import torch
from transformers import AutoFeatureExtractor, AutoModelForImageClassification
import PIL.Image as Image
import os
import sys
from pathlib import Path
import numpy as np

# Add parent directory to path to allow imports from parent
sys.path.append(str(Path(__file__).parent.parent))

class HuggingFaceYogaClassifier:
    def __init__(self, model_name="AdityasArsenal/finetuned-for-YogaPosesv4"):
        """
        Initialize the Hugging Face yoga pose classifier.
        
        Args:
            model_name (str): The name of the Hugging Face model to use.
        """
        print(f"Loading Hugging Face model: {model_name}")
        self.model_name = model_name
        
        # Load feature extractor and model
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
        self.model = AutoModelForImageClassification.from_pretrained(model_name)
        
        # Set model to evaluation mode
        self.model.eval()
        
        print(f"Model loaded successfully with {len(self.model.config.id2label)} yoga pose classes")
        self.id2label = self.model.config.id2label
        
    def predict(self, image_path=None, image=None):
        """
        Predict the yoga pose from an image.
        
        Args:
            image_path (str, optional): Path to the image file.
            image (Image, optional): PIL Image object.
            
        Returns:
            dict: A dictionary containing the predicted pose and confidence.
        """
        if image is None and image_path is not None:
            if not os.path.exists(image_path):
                return {"error": f"Image not found at {image_path}"}
            try:
                image = Image.open(image_path).convert("RGB")
            except Exception as e:
                return {"error": f"Error opening image: {str(e)}"}
        
        if image is None:
            return {"error": "No image provided"}
        
        try:
            # Extract features
            inputs = self.feature_extractor(images=image, return_tensors="pt")
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                
            # Get predicted class
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=1)
            
            # Get top 3 predictions
            top_k = min(3, probabilities.shape[1])
            top_probs, top_indices = torch.topk(probabilities, top_k, dim=1)
            
            # Format results
            predictions = []
            for i in range(top_k):
                idx = top_indices[0][i].item()
                prob = top_probs[0][i].item()
                class_name = self.id2label[str(idx)]
                predictions.append({
                    "pose": class_name,
                    "confidence": prob * 100  # Convert to percentage
                })
            
            return {
                "top_prediction": predictions[0],
                "all_predictions": predictions
            }
            
        except Exception as e:
            return {"error": f"Prediction error: {str(e)}"}
    
    def get_available_classes(self):
        """
        Get all available yoga pose classes from the model.
        
        Returns:
            list: List of class names.
        """
        return list(self.id2label.values())


# Example usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Predict yoga poses using Hugging Face model")
    parser.add_argument("--image", type=str, help="Path to the image file")
    args = parser.parse_args()
    
    image_path = args.image if args.image else "../assets/photo1.png"
    
    classifier = HuggingFaceYogaClassifier()
    result = classifier.predict(image_path=image_path)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        top_pred = result["top_prediction"]
        print(f"Top prediction: {top_pred['pose']} with {top_pred['confidence']:.2f}% confidence")
        
        print("\nAll predictions:")
        for i, pred in enumerate(result["all_predictions"], 1):
            print(f"{i}. {pred['pose']}: {pred['confidence']:.2f}%")
            
    print("\nAvailable classes:")
    classes = classifier.get_available_classes()
    print(f"The model can classify {len(classes)} yoga poses")