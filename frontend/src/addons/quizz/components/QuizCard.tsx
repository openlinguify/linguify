// src/addons/quizz/components/QuizCard.tsx
'use client';

import React from 'react';
import { Clock, Users, Trophy, Star } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface QuizCardProps {
  id: number;
  title: string;
  description?: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  timeLimit?: number;
  questionCount: number;
  isPublic: boolean;
  creatorName: string;
  onStart: (id: number) => void;
  onEdit?: (id: number) => void;
}

const difficultyColors = {
  easy: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  hard: 'bg-red-100 text-red-800',
};

const difficultyLabels = {
  easy: 'Facile',
  medium: 'Moyen',
  hard: 'Difficile',
};

export const QuizCard: React.FC<QuizCardProps> = ({
  id,
  title,
  description,
  category,
  difficulty,
  timeLimit,
  questionCount,
  isPublic,
  creatorName,
  onStart,
  onEdit,
}) => {
  return (
    <Card className="hover:shadow-lg transition-all duration-200 border-l-4 border-l-purple-500">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold text-gray-900 mb-1">
              {title}
            </CardTitle>
            <CardDescription className="text-sm text-gray-600">
              {description || 'Aucune description'}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-xs">
              {category}
            </Badge>
            <Badge className={`text-xs ${difficultyColors[difficulty]}`}>
              {difficultyLabels[difficulty]}
            </Badge>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="space-y-3">
          {/* Quiz metadata */}
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <Trophy className="h-4 w-4" />
              <span>{questionCount} questions</span>
            </div>
            {timeLimit && (
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                <span>{timeLimit} min</span>
              </div>
            )}
            <div className="flex items-center gap-1">
              <Users className="h-4 w-4" />
              <span>{isPublic ? 'Public' : 'Privé'}</span>
            </div>
          </div>

          {/* Creator info */}
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Star className="h-3 w-3" />
            <span>Par {creatorName}</span>
          </div>

          {/* Action buttons */}
          <div className="flex gap-2 pt-2">
            <Button
              onClick={() => onStart(id)}
              className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
            >
              Commencer
            </Button>
            {onEdit && (
              <Button
                variant="outline"
                onClick={() => onEdit(id)}
                className="px-4"
              >
                Modifier
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default QuizCard;