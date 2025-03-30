# Running with Python 3.12

If you're using Python 3.12 and experiencing issues, follow these special instructions:

## Installation Steps

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate it:
   ```
   .\venv\Scripts\activate
   ```

3. Install dependencies manually (one by one):
   ```
   pip install flask==2.3.3
   pip install Werkzeug==2.3.7
   pip install numpy==1.24.3
   pip install matplotlib==3.7.2
   pip install pygame==2.5.2
   pip install pyttsx3==2.90
   pip install gtts==2.3.2
   ```

4. Install TensorFlow (CPU version recommended for Python 3.12):
   ```
   pip install tensorflow-cpu==2.13.0
   pip install tensorflow-hub==0.14.0
   ```

5. Install computer vision packages:
   ```
   pip install opencv-python==4.8.1.78
   pip install mediapipe==0.10.5
   ```

## Known Issues with Python 3.12

- The `playsound` package is not compatible with Python 3.12. The application uses `pygame` for audio playback instead.
- Some TensorFlow operations might not be fully optimized for Python 3.12.

## Alternative: Use Python 3.10

For the best compatibility, consider using Python 3.10:

1. Install Python 3.10 from the [Python website](https://www.python.org/downloads/release/python-3107/)
2. Create a virtual environment with Python 3.10:
   ```
   py -3.10 -m venv venv
   ```
3. Follow the standard installation procedure using `run.bat`
