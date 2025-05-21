import React, { useState, useEffect } from 'react';

interface PoseMeterProps {
  pose: string;
  isInCorrectPose?: boolean;
  duration?: number; // Required hold duration in seconds
  onCompletion?: () => void;
}

interface CompletionTimes {
  [key: string]: number;
}

const PoseMeter: React.FC<PoseMeterProps> = ({
  pose,
  isInCorrectPose = false,
  duration,
  onCompletion
}) => {
  const [progress, setProgress] = useState(0);
  const [holdStartTime, setHoldStartTime] = useState<number | null>(null);
  const [holdTime, setHoldTime] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [showCompletionMessage, setShowCompletionMessage] = useState(false);

  // Define required hold times for different poses (in seconds)
  const completionTimes: CompletionTimes = {
    'vrksana': 30,        // Tree pose - moderate difficulty
    'adhomukha': 45,      // Downward dog - moderate difficulty 
    'balasana': 60,       // Child's pose - relaxation pose, longer hold
    'tadasan': 20,        // Mountain pose - simple pose
    'trikonasana': 40,    // Triangle pose - moderate difficulty
    'virabhadrasana': 35, // Warrior pose - moderate difficulty
    'bhujangasana': 40,   // Cobra pose - moderate difficulty
    'setubandhasana': 50, // Bridge pose - moderate difficulty
    'uttanasana': 35,     // Standing forward bend - moderate difficulty
    'shavasana': 120,     // Corpse pose - meditation pose, longer hold
    'ardhamatsyendrasana': 45  // Half lord of the fishes - moderate difficulty
  };

  // Get required hold time for current pose or use provided value
  const holdDuration = duration || completionTimes[pose] || 30;

  // Reset when pose changes
  useEffect(() => {
    setProgress(0);
    setHoldStartTime(null);
    setHoldTime(0);
    setCompleted(false);
    setShowCompletionMessage(false);
  }, [pose]);

  // Process pose hold status
  useEffect(() => {
    let intervalId: number;
    
    if (isInCorrectPose) {
      // If just entered correct pose
      if (holdStartTime === null) {
        setHoldStartTime(Date.now());
      }
      
      // Start timer to update progress
      intervalId = window.setInterval(() => {
        if (holdStartTime) {
          const currentHoldTime = (Date.now() - holdStartTime) / 1000; // in seconds
          setHoldTime(currentHoldTime);
          
          // Calculate progress percentage
          const newProgress = (currentHoldTime / holdDuration) * 100;
          setProgress(Math.min(100, newProgress));
          
          // Check if pose is completed
          if (currentHoldTime >= holdDuration && !completed) {
            setCompleted(true);
            setShowCompletionMessage(true);
            if (onCompletion) onCompletion();
            
            // Hide completion message after 5 seconds
            setTimeout(() => {
              setShowCompletionMessage(false);
            }, 5000);
          }
        }
      }, 100);
    } else {
      // Add hysteresis - only reset after 3 seconds of incorrect pose
      if (holdStartTime) {
        intervalId = window.setInterval(() => {
          const timeSinceHoldStarted = (Date.now() - holdStartTime) / 1000;
          
          // If we've been in the incorrect pose for more than 3 seconds, reset
          if (!isInCorrectPose && timeSinceHoldStarted > 3) {
            setHoldStartTime(null);
            // Don't reset progress completely to avoid jumpiness
            // Instead, gradually decrease progress
            setProgress(prev => Math.max(0, prev - 2));
          }
        }, 100);
      }
    }
    
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isInCorrectPose, holdStartTime, holdDuration, completed, onCompletion]);

  // If no progress to show, don't render
  if (!isInCorrectPose && holdTime === 0 && !completed) {
    return null;
  }

  // Show completion message
  if (showCompletionMessage) {
    return (
      <div className="w-full bg-green-100 p-4 rounded-md mb-4 text-center animate-pulse">
        <h3 className="text-green-700 font-bold text-xl mb-2">Pose Completed!</h3>
        <p className="text-green-600">Great job! You've successfully held the pose.</p>
      </div>
    );
  }

  return (
    <div className="w-full bg-gray-100 p-4 rounded-md mb-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-gray-700 font-medium">Pose Progress</h3>
        <span className="text-xs text-gray-500">
          {Math.round(holdTime)}s / {holdDuration}s
        </span>
      </div>
      
      <div className="w-full h-4 bg-gray-200 rounded-full">
        <div 
          className="h-full rounded-full bg-green-500 transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
      
      <div className="mt-2 text-sm text-gray-600">
        {isInCorrectPose ? (
          <span className="text-green-600">
            Hold for {Math.max(0, Math.ceil(holdDuration - holdTime))}s more
          </span>
        ) : (
          <span className="text-amber-600">
            Adjust your pose to match the target position
          </span>
        )}
      </div>
    </div>
  );
};

export default PoseMeter;