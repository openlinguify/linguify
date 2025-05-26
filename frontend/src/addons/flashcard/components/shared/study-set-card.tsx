// Placeholder component for study-set-card
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface StudySetCardProps {
  studySet: {
    id: string;
    title: string;
    description?: string;
    [key: string]: any;
  };
}

const StudySetCard: React.FC<StudySetCardProps> = ({ studySet }) => {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <CardTitle className="text-lg">{studySet.title}</CardTitle>
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