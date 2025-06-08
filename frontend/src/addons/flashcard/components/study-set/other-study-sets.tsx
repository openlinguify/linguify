import React from "react";

import { FlashcardDeck } from "@/addons/flashcard/types";

// TODO: Replace with appropriate RouterOutputs type
type RouterOutputs = {
  studySet: {
    byId: {
      user: {
        studySets: Array<{
          id: string;
          title: string;
          description?: string;
        }>;
      };
    };
  };
};

import StudySetCard from "../shared/study-set-card";

interface OtherStudySetsProps {
  studySets: RouterOutputs["studySet"]["byId"]["user"]["studySets"];
}

const OtherStudySets = ({ studySets }: OtherStudySetsProps) => {
  // Convert mock data to FlashcardDeck format
  const convertToFlashcardDeck = (set: RouterOutputs["studySet"]["byId"]["user"]["studySets"][0]): FlashcardDeck => ({
    id: parseInt(set.id),
    name: set.title,
    description: set.description || "",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    is_active: true,
    deck: parseInt(set.id),
    front_text: "",
    back_text: "",
    learned: false,
    last_reviewed: null,
    review_count: 0,
    next_review: null,
  });

  return (
    <div>
      <span className="mb-5 block text-lg font-bold">
        Other sets by this creator
      </span>
      <div className="grid gap-4 md:grid-cols-2">
        {studySets.map((set) => (
          <StudySetCard key={set.id} studySet={convertToFlashcardDeck(set)} />
        ))}
      </div>
    </div>
  );
};

export default OtherStudySets;
