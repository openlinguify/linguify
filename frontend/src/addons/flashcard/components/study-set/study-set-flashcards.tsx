"use client";

import { useParams } from "next/navigation";

// TODO: Replace with appropriate Session type
type Session = {
  user: {
    id: string;
  };
} | null;

interface StudySetData {
  id: string;
  title: string;
  description: string;
  user: { id: string; name: string; image: string | null };
  flashcards: Array<{ id: string; term: string; definition: string }>;
}

// import { api } from "~/trpc/react";
import { api } from "../../api/placeholder-api";
// import FlashcardCard from "../shared/flashcard-card";

const StudySetFlashcards = ({ session }: { session: Session | null }) => {
  console.log('Session:', session); // Keep session usage for future functionality
  const { id }: { id: string } = useParams();
  const { data } = api.studySet.byId.useQuery({ id }) as { data: StudySetData | null };

  return (
    <div className="mb-8">
      <span className="mb-5 inline-block text-lg font-bold">
        Terms in this set ({data?.flashcards?.length || 0})
      </span>
      <div className="flex flex-col gap-3">
        {data?.flashcards?.map((flashcard, index: number) => (
          <div key={index} className="p-4 border rounded-lg">
            <div className="font-semibold">{flashcard.term}</div>
            <div className="text-gray-600">{flashcard.definition}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StudySetFlashcards;
