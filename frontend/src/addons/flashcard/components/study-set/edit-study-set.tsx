"use client";

import React from "react";

// TODO: Replace with appropriate RouterOutputs type
type RouterOutputs = {
  studySet: {
    byId: {
      id: string;
      title: string;
      description?: string | null;
    } | null;
  };
};

// import { api } from "~/trpc/react";
import { api } from "../../api/placeholder-api";
import StudySetForm from "./study-set-form";

const EditStudySet = ({
  studySet,
}: {
  studySet: RouterOutputs["studySet"]["byId"];
}) => {
  const { data } = api.studySet.byId.useQuery(
    { id: studySet?.id ?? "" },
    { initialData: studySet },
  );

  if (!studySet) {
    return <div>Study set not found</div>;
  }

  return (
    <StudySetForm
      defaultValues={{
        ...data,
        description: (data && typeof data === 'object' && 'description' in data) 
          ? (data as { description?: string | null }).description ?? undefined 
          : undefined,
      }}
    />
  );
};

export default EditStudySet;
