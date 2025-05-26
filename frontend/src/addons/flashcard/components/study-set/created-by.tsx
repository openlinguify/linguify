import React from "react";
import Link from "next/link";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import type { RouterOutputs } from "../../api/placeholder-api";

const CreatedBy = ({
  user,
}: {
  user: RouterOutputs["studySet"]["byId"]["user"];
}) => {
  if (!user) return null;
  
  const { id, image, name } = user;

  return (
    <Link href={`/users/${id}`} className="flex items-center gap-4" legacyBehavior>
      <Avatar>
        <AvatarImage src={image ?? undefined} alt="" />
        <AvatarFallback>{name?.at(0)}</AvatarFallback>
      </Avatar>
      <div className="flex flex-col">
        <span className="text-xs font-semibold">Created by</span>
        <span className="text-sm font-medium">{name}</span>
      </div>
    </Link>
  );
};

export default CreatedBy;
