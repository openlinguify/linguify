import React from "react";

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
  return (
    <div>
      <span className="mb-5 block text-lg font-bold">
        Other sets by this creator
      </span>
      <div className="grid gap-4 md:grid-cols-2">
        {studySets.map((set) => (
          <StudySetCard key={set.id} studySet={set} />
        ))}
      </div>
    </div>
  );
};

export default OtherStudySets;
