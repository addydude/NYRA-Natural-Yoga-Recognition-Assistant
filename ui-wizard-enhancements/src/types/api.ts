// Type definitions for the API

/**
 * Represents a yoga pose
 */
export interface YogaPose {
  id: string;
  name: string;
  sanskritName?: string;
  englishName?: string;
  description: string;
  benefits: string[];
  instructions: string[];
  cautions: string[];
  imageSrc: string;
  gifName: string;
}

/**
 * Represents the accuracy data for analytics
 */
export interface AccuracyData {
  values: number[];
  labels: string[];
  poses?: string[];
  period?: string;
}

/**
 * Represents user preferences for personalization
 */
export interface UserPreferences {
  favoritePoises?: string[];
  difficultyLevel?: 'beginner' | 'intermediate' | 'advanced';
  practiceFrequency?: 'daily' | 'few_times_week' | 'weekly' | 'occasionally';
  notifications?: boolean;
  theme?: 'light' | 'dark' | 'system';
  preferredSessionDuration?: number; // in minutes
  focusAreas?: string[]; // e.g., ['balance', 'flexibility', 'strength']
  lastPracticed?: Record<string, string>; // Map of pose IDs to ISO date strings
}

/**
 * Represents breathing pattern data for a pose
 */
export interface BreathingPattern {
  totalCycle: number;  // Total breathing cycle in seconds
  inhaleRatio: number; // Ratio of inhale time to total cycle
}

/**
 * Map of pose IDs to their breathing patterns
 */
export const breathingPatterns: Record<string, BreathingPattern> = {
  'vrksana': { totalCycle: 6, inhaleRatio: 0.4 },       // Tree pose: 2.4s inhale, 3.6s exhale
  'adhomukha': { totalCycle: 8, inhaleRatio: 0.5 },     // Downward dog: 4s inhale, 4s exhale 
  'balasana': { totalCycle: 10, inhaleRatio: 0.3 },     // Child's pose: 3s inhale, 7s exhale (more relaxed)
  'tadasan': { totalCycle: 5, inhaleRatio: 0.5 },       // Mountain pose: 2.5s inhale, 2.5s exhale
  'trikonasana': { totalCycle: 7, inhaleRatio: 0.4 },   // Triangle pose: 2.8s inhale, 4.2s exhale
  'virabhadrasana': { totalCycle: 6, inhaleRatio: 0.45 } // Warrior pose: 2.7s inhale, 3.3s exhale
};

/**
 * Represents a completed yoga session
 */
export interface YogaSession {
  id?: string;
  poseId: string;
  poseName?: string;
  duration: number; // in seconds
  accuracy: number; // percentage from 0-100
  timestamp: string; // ISO date string
}

/**
 * Represents progress data points for visualization
 */
export interface ProgressData {
  sessions: {
    count: number;
    totalDuration: number; // in seconds
    averageAccuracy: number; // percentage from 0-100
    byPose: Record<string, {
      count: number;
      totalDuration: number;
      averageAccuracy: number;
    }>
  };
  timeline: {
    dates: string[]; // ISO date strings
    counts: number[];
    accuracy: number[];
  };
  improvements: {
    mostImproved: string; // pose ID
    overallImprovement: number; // percentage
  }
}

/**
 * Represents a yoga practice routine with multiple poses
 */
export interface PracticeRoutine {
  id: string;
  name: string;
  description?: string;
  poses: Array<{
    poseId: string;
    poseName?: string;
    durationSeconds: number;
    instructions?: string[];
  }>;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  totalDurationMinutes: number;
  tags: string[];
  createdAt: string;
  isCustom?: boolean;
}

/**
 * Represents recommendation data for poses
 */
export interface PoseRecommendation {
  pose: YogaPose;
  reason: string; // e.g., "Based on your recent practice", "To improve balance"
  confidenceScore: number; // 0-1 score representing how confident the system is in this recommendation
}