@echo off
echo Yoga Pose Detection System - Choose Your Detection Method
echo =====================================================
echo 1. Standard detection (TensorFlow/MediaPipe)
echo 2. Hybrid detection (TensorFlow/MediaPipe + HuggingFace)
echo 3. HuggingFace-only detection (No TensorFlow/MediaPipe)
echo =====================================================
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Starting standard detection with TensorFlow/MediaPipe...
    python app.py
) else if "%choice%"=="2" (
    echo Starting hybrid detection with TensorFlow/MediaPipe and HuggingFace...
    python app_hybrid.py
) else if "%choice%"=="3" (
    echo Starting HuggingFace-only detection...
    python app_hf.py
) else (
    echo Invalid choice. Please run the script again and select 1, 2, or 3.
    pause
    exit /b
)