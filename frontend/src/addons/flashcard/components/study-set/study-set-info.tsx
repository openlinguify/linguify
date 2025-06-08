"use client";

import React from "react";
import { useParams } from "next/navigation";

// import { api } from "~/trpc/react";
import { api } from "../../api/placeholder-api";

interface StudySetData {
  id: string;
  title: string;
  description: string;
  user: { id: string; name: string; image: string | null };
  flashcards: Array<{ id: string; term: string; definition: string }>;
}

const StudySetInfo = () => {
  const { id }: { id: string } = useParams();
  const { data } = api.studySet.byId.useQuery({ id }) as { data: StudySetData | null };

  if (!data) {
    return null;
  }

  const { title, description } = data;

  return (
    <div className="mb-4">
      <h1 className="mb-0 text-2xl font-bold sm:text-3xl">{title}</h1>
      {description && <p>{description}</p>}
    </div>
  );
};

export default StudySetInfo;
