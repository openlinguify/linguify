import Link from "next/link";
import { Edit } from "lucide-react";

// TODO: Replace with appropriate Session type
type Session = any;

import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

import StudySetFoldersDialog from "./study-set-folders-dialog";
import StudySetOptionsDropdown from "./study-set-options-dropdown";
import StudySetShareDialog from "./study-set-share-dialog";

interface StudySetCTAProps {
  session: Session | null;
  id: string;
  userId: string;
}

const StudySetCTA = ({ session, id, userId }: StudySetCTAProps) => {
  return (
    <div className="flex gap-2">
      {session && <StudySetFoldersDialog session={session} />}
      {session?.user.id === userId && (
        <TooltipProvider>
          <Tooltip>
            <Link href={`/study-sets/${id}/edit`} legacyBehavior>
              <TooltipTrigger asChild>
                <Button size="icon" variant="outline">
                  <Edit size={16} />
                  <span className="sr-only">Edit</span>
                </Button>
              </TooltipTrigger>
            </Link>
            <TooltipContent>
              <p>Edit</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )}
      <StudySetShareDialog id={id} />
      <StudySetOptionsDropdown
        id={id}
        isOwner={session?.user.id === userId}
        userId={session?.user.id}
      />
    </div>
  );
};

export default StudySetCTA;
