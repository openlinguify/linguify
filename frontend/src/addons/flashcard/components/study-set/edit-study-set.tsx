"use client";

import React from "react";

// TODO: Replace with appropriate RouterOutputs type
type RouterOutputs = {
  studySet: {
    byId: {
      id: string;
      title: string;
      description?: string | null;
    };
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
    { id: studySet.id },
    { initialData: studySet },
  );

  return (
    <StudySetForm
      defaultValues={{
        ...data,
        description: data.description ?? undefined,
      }}
    />
  );
};

export default EditStudySet;
