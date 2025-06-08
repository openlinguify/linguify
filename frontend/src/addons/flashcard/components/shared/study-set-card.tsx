// Placeholder component for study-set-card
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FlashcardDeck } from '@/addons/flashcard/types';

interface StudySetCardProps {
  studySet: FlashcardDeck;
}

const StudySetCard: React.FC<StudySetCardProps> = ({ studySet }) => {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <CardTitle className="text-lg">{studySet.name}</CardTitle>
      </CardHeader>
      <CardContent>
        {studySet.description && (
          <p className="text-gray-600">{studySet.description}</p>
        )}
        <div className="mt-2 text-sm text-gray-500">
          Study Set ID: {studySet.id}
        </div>
      </CardContent>
    </Card>
  );
};

export default StudySetCard;