// src/app/(dashboard)/(apps)/flashcard/_components/StudyModes.tsx

import React from "react";
import Link from "next/link";
import { Clock, BookOpen, Dumbbell, Layers } from "lucide-react";

interface StudyModeProps {
  deckId: number;
}

interface StudyModeCardProps {
  name: string;
  description: string;
  icon: React.ReactNode;
  path: string;
  deckId: number;
}

const StudyModeCard = ({
  name,
  description,
  icon,
  path,
  deckId,
}: StudyModeCardProps) => {
  return (
    <Link
      href={`/flashcard/${path}/${deckId}`}
      className="flex items-center gap-3 p-4 border rounded-lg hover:bg-gray-50 transition-colors"
    >
      <div className="rounded-md p-2 bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400">
        {icon}
      </div>
      <div>
        <h4 className="font-medium text-sm">{name}</h4>
        <p className="text-xs text-gray-500">{description}</p>
      </div>
    </Link>
  );
};

export default function StudyModes({ deckId }: StudyModeProps) {
  return (
    <div className="mb-8">
      <h3 className="text-base font-semibold mb-4">Study Modes</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <StudyModeCard
          name="Flashcards"
          description="Flip between terms and definitions"
          icon={<Layers className="h-5 w-5 text-white" />}
          path="flashcards"
          deckId={deckId}
        />
        <StudyModeCard
          name="Learn"
          description="Adaptive multiple choice questions"
          icon={<BookOpen className="h-5 w-5 text-white" />}
          path="learn"
          deckId={deckId}
        />
        <StudyModeCard
          name="Match"
          description="Match terms with definitions quickly"
          icon={<Clock className="h-5 w-5 text-white" />}
          path="match"
          deckId={deckId}
        />
        <StudyModeCard
          name="Review"
          description="Spaced repetition for better retention"
          icon={<Dumbbell className="h-5 w-5 text-white" />}
          path="review"
          deckId={deckId}
        />
      </div>
    </div>
  );
}