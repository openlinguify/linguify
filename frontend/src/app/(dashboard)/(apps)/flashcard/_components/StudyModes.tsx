// src/app/(dashboard)/(apps)/flashcard/_components/StudyModes.tsx
import React from "react";
import Link from "next/link";
import { Clock, BookOpen, FlaskConical, Dumbbell, TimerOff, Layers } from "lucide-react";

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
      className="p-6 border rounded-lg transition-colors hover:border-brand-purple cursor-pointer flex flex-col group"
    >
      <div className="flex justify-between items-center mb-4">
        <div className="text-brand-purple p-2 bg-brand-purple/10 rounded-lg">
          {icon}
        </div>
        <div className="text-xs italic text-gray-400">Study Mode</div>
      </div>
      <div className="font-semibold text-lg mb-2 group-hover:text-brand-purple transition-colors">{name}</div>
      <div className="text-sm text-gray-600">{description}</div>
    </Link>
  );
};

export default function StudyModes({ deckId }: StudyModeProps) {
  return (
    <div className="mb-8">
      <h3 className="text-xl font-semibold mb-4">Choose a Study Mode</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <StudyModeCard
          name="Flashcards"
          description="Classic flashcards. Test your knowledge by flipping between the term and definition."
          icon={<Layers size={20} />}
          path="flashcards"
          deckId={deckId}
        />
        <StudyModeCard
          name="Learn"
          description="Multiple choice questions that adapt to your learning. Master terms at your own pace."
          icon={<BookOpen size={20} />}
          path="learn"
          deckId={deckId}
        />
        <StudyModeCard
          name="Match"
          description="Race against the clock to match terms with definitions as quickly as possible."
          icon={<Clock size={20} />}
          path="match"
          deckId={deckId}
        />
        <StudyModeCard
          name="Review"
          description="Smart repetition algorithm that focuses on the cards you need to review. Optimized for long-term retention."
          icon={<Dumbbell size={20} />}
          path="review"
          deckId={deckId}
        />
      </div>
    </div>
  );
}