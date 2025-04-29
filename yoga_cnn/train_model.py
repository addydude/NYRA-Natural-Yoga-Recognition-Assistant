import os
import json
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from datetime import datetime
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from yoga_classifier import create_yoga_pose_classifier, fine_tune_model
from dataset_loader import load_yoga_dataset, save_class_indices

# Directory configurations
OUTPUT_DIR = os.path.join(r"D:\NYRAGGbackup - Copy\yoga_cnn", "processed_dataset")
MODEL_DIR = os.path.join(r"D:\NYRAGGbackup - Copy\yoga_cnn", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# Training parameters
BATCH_SIZE = 32
IMG_SIZE = (224, 224)
EPOCHS = 20
FINE_TUNE_EPOCHS = 10
MODEL_SIZE = 'small'  # 'small' or 'large'

def plot_training_history(history):
    """Plot training & validation accuracy/loss"""
    plt.figure(figsize=(12, 4))
    
    # For combined history dictionaries
    if isinstance(history, dict):
        # Plot accuracy subplot
        plt.subplot(1, 2, 1)
        plt.plot(history['accuracy'])
        plt.plot(history['val_accuracy'])
        plt.title('Model Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend(['Train', 'Validation'], loc='upper left')
        
        # Plot loss subplot
        plt.subplot(1, 2, 2)
        plt.plot(history['loss'])
        plt.plot(history['val_loss'])
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend(['Train', 'Validation'], loc='upper left')
    
    # For keras History objects
    else:
        # Plot accuracy subplot
        plt.subplot(1, 2, 1)
        plt.plot(history.history['accuracy'])
        plt.plot(history.history['val_accuracy'])
        plt.title('Model Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend(['Train', 'Validation'], loc='upper left')
        
        # Plot loss subplot
        plt.subplot(1, 2, 2)
        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend(['Train', 'Validation'], loc='upper left')
    
    plt.tight_layout()
    plt.savefig(os.path.join(MODEL_DIR, 'training_history.png'))
    print(f"Training history plot saved to {os.path.join(MODEL_DIR, 'training_history.png')}")

def train_model():
    """Train a MobileNetV3-based model for yoga pose classification"""
    print("Starting yoga pose classification model training...")
    
    # Define directories
    train_dir = os.path.join(OUTPUT_DIR, 'train')
    val_dir = os.path.join(OUTPUT_DIR, 'val')
    
    if not os.path.exists(train_dir) or not os.path.exists(val_dir):
        raise FileNotFoundError(f"Training/validation directories not found. Please run dataset_loader.py first.")
    
    # Create data generators
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    # Only rescaling for validation
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    # Create generators
    print("Loading training data...")
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )
    
    print("Loading validation data...")
    val_generator = val_datagen.flow_from_directory(
        val_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )
    
    # Save class indices for inference
    class_indices_path = os.path.join(MODEL_DIR, 'class_indices.json')
    class_indices = train_generator.class_indices
    save_class_indices(class_indices, class_indices_path)
    
    # Print class mapping
    print("Class mapping:")
    for cls_name, idx in class_indices.items():
        print(f"  {idx}: {cls_name}")
    
    num_classes = len(class_indices)
    print(f"Training model to classify {num_classes} yoga poses")
    
    # Create the model
    print(f"Creating MobileNetV3-{MODEL_SIZE} model...")
    model = create_yoga_pose_classifier(num_classes, MODEL_SIZE)
    model.summary()
    
    # Set up callbacks
    callbacks = [
        ModelCheckpoint(
            os.path.join(MODEL_DIR, 'yoga_model_best.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=3,
            min_lr=0.00001,
            verbose=1
        )
    ]
    
    # Initial training phase
    print(f"Starting initial training for {EPOCHS} epochs...")
    history1 = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        validation_data=val_generator,
        validation_steps=val_generator.samples // BATCH_SIZE,
        epochs=EPOCHS,
        callbacks=callbacks
    )
    
    # Fine-tuning phase
    print("Fine-tuning the model...")
    fine_tuned_model = fine_tune_model(model)
    
    # Train with fine-tuning
    print(f"Training fine-tuned model for {FINE_TUNE_EPOCHS} epochs...")
    history2 = fine_tuned_model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        validation_data=val_generator,
        validation_steps=val_generator.samples // BATCH_SIZE,
        epochs=FINE_TUNE_EPOCHS,
        callbacks=callbacks
    )
    
    # Combine histories for plotting
    combined_history = {}
    for key in history1.history:
        combined_history[key] = history1.history[key] + history2.history[key]
    
    # Save the final model
    model_path = os.path.join(MODEL_DIR, 'yoga_model_final.h5')
    fine_tuned_model.save(model_path)
    print(f"Final model saved to {model_path}")
    
    # Save TensorFlow Lite model for mobile deployment
    tflite_path = os.path.join(MODEL_DIR, 'yoga_model.tflite')
    converter = tf.lite.TFLiteConverter.from_keras_model(fine_tuned_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    print(f"TFLite model saved to {tflite_path}")
    
    # Plot training history
    plot_training_history(combined_history)
    
    # Evaluate the model
    print("\nEvaluating model on validation data...")
    val_loss, val_acc = fine_tuned_model.evaluate(val_generator)
    print(f"Validation accuracy: {val_acc:.4f}")
    print(f"Validation loss: {val_loss:.4f}")
    
    return fine_tuned_model

if __name__ == "__main__":
    # Enable memory growth for GPU training
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"Using {len(gpus)} GPU(s) for training")
        except RuntimeError as e:
            print(f"Error setting up GPU: {e}")
    else:
        print("No GPU found. Using CPU for training.")
    
    # Print TensorFlow version
    print(f"TensorFlow version: {tf.__version__}")
    
    # Train the model
    model = train_model()