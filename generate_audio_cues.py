"""
Generate audio cues for yoga breathing
"""

import os
from gtts import gTTS
import pygame

def generate_audio_files():
    """Generate audio cues for breathing instructions"""
    
    print("Generating audio cues for yoga breathing...")
    
    # Create directory if it doesn't exist
    audio_dir = os.path.join(os.path.dirname(__file__), 'static', 'audio')
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
        print(f"Created directory: {audio_dir}")
    
    # Generate inhale audio
    inhale_path = os.path.join(audio_dir, 'inhale.mp3')
    if not os.path.exists(inhale_path):
        try:
            tts = gTTS("Inhale deeply", lang='en', slow=False)
            tts.save(inhale_path)
            print(f"Created inhale audio file: {inhale_path}")
        except Exception as e:
            print(f"Error creating inhale audio: {str(e)}")
    
    # Generate exhale audio
    exhale_path = os.path.join(audio_dir, 'exhale.mp3')
    if not os.path.exists(exhale_path):
        try:
            tts = gTTS("Exhale slowly", lang='en', slow=False)
            tts.save(exhale_path)
            print(f"Created exhale audio file: {exhale_path}")
        except Exception as e:
            print(f"Error creating exhale audio: {str(e)}")
    
    # Test audio playback
    try:
        pygame.mixer.init()
        print("Testing audio playback...")
        
        print("Playing inhale sound...")
        pygame.mixer.music.load(inhale_path)
        pygame.mixer.music.play()
        pygame.time.wait(2000)  # Wait for 2 seconds
        
        print("Playing exhale sound...")
        pygame.mixer.music.load(exhale_path)
        pygame.mixer.music.play()
        pygame.time.wait(2000)  # Wait for 2 seconds
        
        print("Audio test complete!")
    except Exception as e:
        print(f"Audio test failed: {str(e)}")
    
    print("Audio setup complete!")

if __name__ == "__main__":
    generate_audio_files()
