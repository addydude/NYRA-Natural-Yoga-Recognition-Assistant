import React, { useState, useEffect } from 'react';

interface BreathingGuideProps {
  pose: string;
  breathCycle?: number; // Total breathing cycle in seconds
  inhaleRatio?: number; // Ratio of inhale time to total cycle
}

interface BreathingPatterns {
  [key: string]: [number, number]; // [total_cycle_seconds, inhale_ratio]
}

const BreathingGuide: React.FC<BreathingGuideProps> = ({ 
  pose, 
  breathCycle, 
  inhaleRatio 
}) => {
  const [isInhaling, setIsInhaling] = useState(true);
  const [progress, setProgress] = useState(0);
  const [cycleStartTime, setCycleStartTime] = useState(Date.now());
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);
  const [inhaleAudio, setInhaleAudio] = useState<HTMLAudioElement | null>(null);
  const [exhaleAudio, setExhaleAudio] = useState<HTMLAudioElement | null>(null);

  // Define breathing patterns for different yoga poses
  const breathingPatterns: BreathingPatterns = {
    'vrksana': [6, 0.4],       // Tree pose: 2.4s inhale, 3.6s exhale
    'adhomukha': [8, 0.5],     // Downward dog: 4s inhale, 4s exhale 
    'balasana': [10, 0.3],     // Child's pose: 3s inhale, 7s exhale (more relaxed)
    'tadasan': [5, 0.5],       // Mountain pose: 2.5s inhale, 2.5s exhale
    'trikonasana': [7, 0.4],   // Triangle pose: 2.8s inhale, 4.2s exhale
    'virabhadrasana': [6, 0.45], // Warrior pose: 2.7s inhale, 3.3s exhale
    'bhujangasana': [7, 0.4],   // Cobra pose: 2.8s inhale, 4.2s exhale
    'setubandhasana': [8, 0.4], // Bridge pose: 3.2s inhale, 4.8s exhale
    'uttanasana': [6, 0.3],     // Standing forward bend: 1.8s inhale, 4.2s exhale
    'shavasana': [12, 0.3],     // Corpse pose: 3.6s inhale, 8.4s exhale (deeply relaxing)
    'ardhamatsyendrasana': [7, 0.4] // Half lord of the fishes pose: 2.8s inhale, 4.2s exhale
  };

  // Get breathing pattern for current pose or use provided values
  const pattern = breathingPatterns[pose] || [6, 0.4]; // Default to vrksana pattern
  const cycle = breathCycle || pattern[0];
  const ratio = inhaleRatio || pattern[1];

  // Initialize audio on component mount
  useEffect(() => {
    const inhaleSound = new Audio('/static/audio/inhale.mp3');
    const exhaleSound = new Audio('/static/audio/exhale.mp3');
    
    setInhaleAudio(inhaleSound);
    setExhaleAudio(exhaleSound);
    
    return () => {
      inhaleSound.pause();
      exhaleSound.pause();
    };
  }, []);

  // Update breathing state
  useEffect(() => {
    const intervalId = setInterval(() => {
      const now = Date.now();
      const elapsedTime = (now - cycleStartTime) / 1000; // Convert to seconds
      
      // Reset cycle when complete
      if (elapsedTime >= cycle) {
        setCycleStartTime(now);
        return;
      }
      
      // Determine if inhaling or exhaling based on position in cycle
      const newIsInhaling = elapsedTime < (cycle * ratio);
      
      // Play audio cue when transitioning between inhale and exhale
      if (newIsInhaling !== isInhaling) {
        if (newIsInhaling && inhaleAudio) {
          if (audio) audio.pause();
          setAudio(inhaleAudio);
          inhaleAudio.currentTime = 0;
          inhaleAudio.play().catch(e => console.error("Audio playback failed:", e));
        } else if (!newIsInhaling && exhaleAudio) {
          if (audio) audio.pause();
          setAudio(exhaleAudio);
          exhaleAudio.currentTime = 0;
          exhaleAudio.play().catch(e => console.error("Audio playback failed:", e));
        }
      }
      
      setIsInhaling(newIsInhaling);
      
      // Calculate progress percentage through current breath phase
      if (newIsInhaling) {
        setProgress(elapsedTime / (cycle * ratio));
      } else {
        setProgress((elapsedTime - cycle * ratio) / (cycle * (1 - ratio)));
      }
    }, 50);
    
    return () => clearInterval(intervalId);
  }, [cycleStartTime, cycle, ratio, isInhaling, audio, inhaleAudio, exhaleAudio]);

  // Reset cycle when pose changes
  useEffect(() => {
    setCycleStartTime(Date.now());
    setIsInhaling(true);
    setProgress(0);
  }, [pose]);

  return (
    <div className="w-full bg-gray-100 p-4 rounded-md mb-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-gray-700 font-medium">Current Pose: <span className="capitalize">{pose}</span></h3>
        <span className="text-xs text-gray-500">Breathing Guide</span>
      </div>
      
      <div className="bg-white p-4 rounded-lg flex flex-col items-center">
        <div className={`text-xl font-bold mb-2 ${isInhaling ? 'text-green-600' : 'text-red-700'}`}>
          {isInhaling ? 'INHALE' : 'EXHALE'}
        </div>
        
        <div className="w-full h-2 bg-gray-200 rounded-full mb-2">
          <div 
            className={`h-full rounded-full ${isInhaling ? 'bg-green-600' : 'bg-red-600'}`}
            style={{ width: `${Math.min(100, Math.max(0, progress * 100))}%` }}
          />
        </div>
        
        <div className="text-xs text-gray-500">
          {isInhaling ? 'Breathe in deeply through your nose' : 'Breathe out slowly through your mouth'}
        </div>
      </div>
    </div>
  );
};

export default BreathingGuide;