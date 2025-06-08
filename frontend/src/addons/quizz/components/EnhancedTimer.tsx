// src/addons/quizz/components/EnhancedTimer.tsx
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Clock, Pause, Play, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

interface EnhancedTimerProps {
  totalTime: number; // in seconds
  onTimeUp: () => void;
  onTimeWarning?: (secondsLeft: number) => void;
  warningThresholds?: number[]; // e.g., [60, 30, 10] for warnings at 1min, 30s, 10s
  allowPause?: boolean;
  autoStart?: boolean;
}

const EnhancedTimer: React.FC<EnhancedTimerProps> = ({
  totalTime,
  onTimeUp,
  onTimeWarning,
  warningThresholds = [60, 30, 10],
  allowPause = true,
  autoStart = true,
}) => {
  const [timeLeft, setTimeLeft] = useState(totalTime);
  const [isRunning, setIsRunning] = useState(autoStart);
  const [isPaused, setIsPaused] = useState(false);
  const [warningsTriggered, setWarningsTriggered] = useState<Set<number>>(new Set());
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Initialize audio for warnings
  useEffect(() => {
    audioRef.current = new Audio('/notification.mp3'); // Add a notification sound file
    audioRef.current.volume = 0.5;
  }, []);

  // Timer logic
  useEffect(() => {
    if (isRunning && !isPaused && timeLeft > 0) {
      intervalRef.current = setInterval(() => {
        setTimeLeft(prev => {
          const newTime = prev - 1;
          
          // Check for warnings
          warningThresholds.forEach(threshold => {
            if (newTime === threshold && !warningsTriggered.has(threshold)) {
              setWarningsTriggered(prev => new Set(prev).add(threshold));
              onTimeWarning?.(newTime);
              
              // Play warning sound
              if (audioRef.current) {
                audioRef.current.play().catch(() => {
                  // Ignore audio play errors (user interaction required)
                });
              }
            }
          });

          // Time up
          if (newTime <= 0) {
            setIsRunning(false);
            onTimeUp();
            return 0;
          }

          return newTime;
        });
      }, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRunning, isPaused, timeLeft, warningThresholds, warningsTriggered, onTimeWarning, onTimeUp]);

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimePercentage = () => {
    return ((totalTime - timeLeft) / totalTime) * 100;
  };

  const getTimerColor = () => {
    if (timeLeft <= 10) return 'text-red-600';
    if (timeLeft <= 30) return 'text-orange-600';
    if (timeLeft <= 60) return 'text-yellow-600';
    return 'text-gray-700';
  };

  const getProgressColor = () => {
    if (timeLeft <= 10) return 'bg-red-500';
    if (timeLeft <= 30) return 'bg-orange-500';
    if (timeLeft <= 60) return 'bg-yellow-500';
    return 'bg-purple-500';
  };

  const handlePauseResume = () => {
    if (isPaused) {
      setIsPaused(false);
      setIsRunning(true);
    } else {
      setIsPaused(true);
      setIsRunning(false);
    }
  };

  const handleStart = () => {
    setIsRunning(true);
    setIsPaused(false);
  };

  const isWarningTime = timeLeft <= Math.max(...warningThresholds);

  return (
    <Card className={`p-4 transition-all duration-300 ${
      isWarningTime ? 'border-red-300 bg-red-50 shadow-lg' : ''
    } ${timeLeft <= 10 ? 'animate-pulse' : ''}`}>
      <div className="flex items-center justify-between">
        
        {/* Timer Display */}
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-full ${
            isWarningTime ? 'bg-red-100' : 'bg-purple-100'
          }`}>
            <Clock className={`h-5 w-5 ${
              isWarningTime ? 'text-red-600' : 'text-purple-600'
            }`} />
          </div>
          
          <div>
            <div className={`text-2xl font-mono font-bold ${getTimerColor()}`}>
              {formatTime(timeLeft)}
            </div>
            <div className="text-xs text-gray-500">
              {isPaused ? 'En pause' : isRunning ? 'En cours' : 'Arrêté'}
            </div>
          </div>
        </div>

        {/* Controls */}
        {allowPause && (
          <div className="flex items-center gap-2">
            {!isRunning && !isPaused ? (
              <Button
                onClick={handleStart}
                size="sm"
                variant="outline"
                className="text-green-600 border-green-600 hover:bg-green-50"
              >
                <Play className="h-4 w-4 mr-1" />
                Démarrer
              </Button>
            ) : (
              <Button
                onClick={handlePauseResume}
                size="sm"
                variant="outline"
                className={isPaused ? 'text-green-600 border-green-600 hover:bg-green-50' : 'text-orange-600 border-orange-600 hover:bg-orange-50'}
              >
                {isPaused ? (
                  <>
                    <Play className="h-4 w-4 mr-1" />
                    Reprendre
                  </>
                ) : (
                  <>
                    <Pause className="h-4 w-4 mr-1" />
                    Pause
                  </>
                )}
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="mt-3">
        <Progress 
          value={getTimePercentage()} 
          className="h-2"
        />
      </div>

      {/* Warning Message */}
      {isWarningTime && (
        <div className="mt-3 flex items-center gap-2 text-red-600 text-sm">
          <AlertTriangle className="h-4 w-4" />
          <span>
            {timeLeft <= 10 
              ? 'Attention ! Plus que quelques secondes !' 
              : 'Dépêchez-vous, le temps s\'épuise !'}
          </span>
        </div>
      )}

      {/* Time Statistics */}
      <div className="mt-3 flex justify-between text-xs text-gray-500">
        <span>Temps écoulé : {formatTime(totalTime - timeLeft)}</span>
        <span>Temps total : {formatTime(totalTime)}</span>
      </div>
    </Card>
  );
};

export default EnhancedTimer;