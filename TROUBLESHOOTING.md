# Troubleshooting Guide for NYRA

This guide provides solutions for common issues you might encounter while setting up or using NYRA.

## Installation Issues

### Python Version Incompatibility

**Problem**: Error message about incompatible Python version.

**Solution**: NYRA works best with Python 3.10 or 3.11. If you're using Python 3.12, follow the special instructions in [PYTHON312.md](./PYTHON312.md).

### Package Installation Fails

**Problem**: Errors when running `pip install -r requirements.txt`

**Solutions**:
- Try installing packages one by one to identify which package is causing the issue
- For Windows users with C++ compiler errors, install Visual C++ Build Tools
- For TensorFlow issues, try installing a different version: `pip install tensorflow==2.12.0`

## Runtime Issues

### Webcam Not Detected

**Problem**: "Cannot open webcam" error when starting the application.

**Solutions**:
- Make sure your webcam is properly connected and not in use by another application
- Grant webcam permission to your terminal/IDE
- Try a different camera by modifying the code in `app.py` - change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` or another index

### WebSocket Server Errors

**Problem**: You see WebSocket errors in the terminal.

**Solution**: 
- The WebSocket server helps with real-time communication but is not critical for the core application
- The application has fallback functionality and will continue to work
- If you need WebSockets, make sure you have installed the required package: `pip install websockets==11.0.3`

### Missing Models or Assets

**Problem**: Error about missing models or assets.

**Solutions**:
- Make sure you ran the application from the project root directory
- The first run might take longer as it downloads required models
- Check if your firewall is blocking downloads from TensorFlow Hub or HuggingFace

## Performance Issues

### Slow Performance

**Problem**: The application runs very slowly.

**Solutions**:
- Try using the standard mode instead of HuggingFace or hybrid mode: `python app.py`
- Lower your webcam resolution by modifying the `make_480p()` function in the code
- Close other resource-intensive applications

### High Memory Usage

**Problem**: The application uses too much memory.

**Solution**: The AI models, especially HuggingFace models, require significant memory. Try:
- Using the standard mode (MediaPipe) which uses less RAM
- Adding a swap file/partition if you're on Linux
- Closing other applications to free up memory

## Application-Specific Issues

### Pose Detection Inaccuracy

**Problem**: The pose detection seems inaccurate.

**Solutions**:
- Make sure you have good lighting in the room
- Wear clothing that contrasts with your background
- Keep the background as simple as possible
- Try the hybrid mode for better accuracy: `python app_hybrid.py`

### Audio Guidance Not Working

**Problem**: You don't hear audio guidance for breathing.

**Solutions**:
- Make sure your system volume is turned up
- Check if audio files were generated in the `static/audio` folder
- Try reinstalling pygame: `pip uninstall pygame` then `pip install pygame==2.5.2`

## Still Having Issues?

If you're still experiencing problems, please:
1. Check the project's GitHub Issues section to see if others have encountered the same problem
2. Create a new Issue with detailed information about your setup and the problem
3. Include steps to reproduce the issue and any error messages you see