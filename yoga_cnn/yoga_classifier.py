import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.applications import MobileNetV3Small, MobileNetV3Large
from tensorflow.keras.applications.mobilenet_v3 import preprocess_input

def create_yoga_pose_classifier(num_classes, size='small'):
    """
    Create a yoga pose classifier using MobileNetV3.
    
    Args:
        num_classes: Number of yoga pose classes
        size: Model size, either 'small' or 'large'
        
    Returns:
        model: Compiled Keras model
    """
    # Create base pre-trained model
    if size.lower() == 'small':
        base_model = MobileNetV3Small(
            weights='imagenet', 
            include_top=False, 
            input_shape=(224, 224, 3)
        )
    else:  # large
        base_model = MobileNetV3Large(
            weights='imagenet', 
            include_top=False, 
            input_shape=(224, 224, 3)
        )
    
    # Initial: Freeze all layers in the base model
    for layer in base_model.layers:
        layer.trainable = False
    
    # Add classifier head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    # Create the full model
    model = Model(inputs=base_model.input, outputs=predictions)
    
    # Compile the model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def fine_tune_model(model, num_layers_to_fine_tune=50):
    """
    Fine-tune the later layers of the model.
    
    Args:
        model: The pre-trained model to fine-tune
        num_layers_to_fine_tune: Number of layers to unfreeze (from the end)
        
    Returns:
        model: Fine-tuned model ready for training
    """
    # Find the base model (MobileNetV3) in the model layers
    # The actual base model is embedded in the functional model
    base_model = None
    for layer in model.layers:
        if 'mobilenetv3' in layer.name.lower():
            base_model = layer
            break
    
    if base_model is None:
        print("Could not find MobileNetV3 base model. Unfreezing all layers.")
        # If we can't identify the base model, unfreeze everything
        for layer in model.layers:
            layer.trainable = True
    else:
        # Only unfreeze the last few layers of the base model
        for layer in base_model.layers[-(num_layers_to_fine_tune or 10):]:
            layer.trainable = True
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def load_and_preprocess_image(image_path, target_size=(224, 224)):
    """
    Load and preprocess an image for yoga pose prediction.
    
    Args:
        image_path: Path to the image file
        target_size: Target image size for the model
    
    Returns:
        img_array: Preprocessed image array ready for prediction
    """
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=target_size)
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return img_array

def predict_yoga_pose(model, image_path, class_indices_path):
    """
    Predict yoga pose for an image.
    
    Args:
        model: Trained yoga pose classifier model
        image_path: Path to the image file
        class_indices_path: Path to the class indices JSON file
    
    Returns:
        prediction: Dictionary with predicted class and confidence
    """
    # Load class indices
    with open(class_indices_path, 'r') as f:
        class_indices = json.load(f)
    
    # Load and preprocess the image
    img_array = load_and_preprocess_image(image_path)
    
    # Make prediction
    predictions = model.predict(img_array)
    predicted_class_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_class_idx])
    
    # Convert numerical index to class name
    predicted_class = class_indices.get(str(predicted_class_idx))
    
    # Return prediction dictionary
    return {
        'class_name': predicted_class,
        'confidence': confidence,
        'top_predictions': [
            {
                'class_name': class_indices.get(str(i)),
                'confidence': float(predictions[0][i])
            }
            for i in predictions[0].argsort()[-3:][::-1]  # Top 3 predictions
        ]
    }

def convert_to_tflite(model_path, output_path):
    """
    Convert a Keras model to TFLite format.
    
    Args:
        model_path: Path to the saved Keras model
        output_path: Path to save the TFLite model
    
    Returns:
        output_path: Path to the saved TFLite model
    """
    # Load the model
    model = tf.keras.models.load_model(model_path)
    
    # Convert to TFLite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    # Save the TFLite model
    with open(output_path, 'wb') as f:
        f.write(tflite_model)
    
    print(f"Model converted to TFLite and saved to {output_path}")
    return output_path

def visualize_prediction(image_path, prediction, output_path=None):
    """
    Visualize an image with its predicted yoga pose and confidence.
    
    Args:
        image_path: Path to the image file
        prediction: Prediction dictionary from predict_yoga_pose
        output_path: Path to save the visualization, if None it will be displayed
    """
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    
    # Load the image
    img = tf.keras.preprocessing.image.load_img(image_path)
    plt.figure(figsize=(10, 10))
    plt.imshow(img)
    
    # Add prediction text
    class_name = prediction['class_name']
    confidence = prediction['confidence']
    plt.title(f"Predicted: {class_name}\nConfidence: {confidence:.2f}")
    
    # Add box with top 3 predictions
    text = "Top Predictions:\n"
    for i, pred in enumerate(prediction['top_predictions']):
        text += f"{i+1}. {pred['class_name']}: {pred['confidence']:.2f}\n"
    
    plt.figtext(0.5, 0.01, text, ha="center", fontsize=10, 
                bbox={"facecolor":"orange", "alpha":0.5, "pad":5})
    
    plt.axis('off')
    
    if output_path:
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

if __name__ == "__main__":
    print("Yoga pose classifier module loaded.")
    print("Use the create_yoga_pose_classifier() function to create a new model.")
    print("Use the predict_yoga_pose() function to make predictions with a trained model.")