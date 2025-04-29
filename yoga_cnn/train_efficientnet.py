import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetV2B0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt
from dataset_loader import load_yoga_dataset

# Set memory growth for GPU to avoid OOM errors
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
NUM_CLASSES = 20
EPOCHS = 10
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'efficientnet')
os.makedirs(MODEL_DIR, exist_ok=True)

def create_model():
    # Load pre-trained EfficientNetV2 with imagenet weights
    base_model = EfficientNetV2B0(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
    
    # Freeze the base model layers
    for layer in base_model.layers:
        layer.trainable = False
        
    # Add classification head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dropout(0.5)(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.3)(x)
    predictions = Dense(NUM_CLASSES, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    
    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train():
    # Load and preprocess data
    (x_train, y_train), (x_val, y_val) = load_yoga_dataset(img_size=IMG_SIZE)
    
    # Create model
    model = create_model()
    print(model.summary())
    
    # Define callbacks
    checkpoint_best = ModelCheckpoint(
        os.path.join(MODEL_DIR, 'yoga_efficientnet_best.h5'),
        monitor='val_accuracy',
        verbose=1,
        save_best_only=True,
        mode='max'
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.1,
        patience=3,
        verbose=1,
        min_lr=1e-5
    )
    
    # Train model
    history = model.fit(
        x_train, y_train,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=(x_val, y_val),
        callbacks=[checkpoint_best, reduce_lr]
    )
    
    # Save final model
    final_model_path = os.path.join(MODEL_DIR, 'yoga_efficientnet_final.h5')
    model.save(final_model_path)
    print(f"Final model saved to {final_model_path}")
    
    # Convert to TFLite for mobile deployment
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    
    tflite_model_path = os.path.join(MODEL_DIR, 'yoga_efficientnet.tflite')
    with open(tflite_model_path, 'wb') as f:
        f.write(tflite_model)
    print(f"TFLite model saved to {tflite_model_path}")
    
    # Plot training history
    plt.figure(figsize=(12, 4))
    
    # Plot accuracy
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training')
    plt.plot(history.history['val_accuracy'], label='Validation')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    
    # Plot loss
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training')
    plt.plot(history.history['val_loss'], label='Validation')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    history_plot_path = os.path.join(MODEL_DIR, 'efficientnet_combined_training_history.png')
    plt.tight_layout()
    plt.savefig(history_plot_path)
    print(f"Training history plot saved to {history_plot_path}")
    
    # Evaluate model on validation data
    print("Evaluating model on validation data...")
    evaluation = model.evaluate(x_val, y_val, verbose=1)
    print(f"Validation accuracy: {evaluation[1]:.4f}")
    print(f"Validation loss: {evaluation[0]:.4f}")

if __name__ == '__main__':
    train()