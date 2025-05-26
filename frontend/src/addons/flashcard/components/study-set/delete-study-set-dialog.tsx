"use client";

import { useRouter } from "next/navigation";
import { Loader2Icon, Trash2Icon } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { toast } from "@/components/ui/use-toast";

// import { api } from "~/trpc/react";
import { api } from "../../api/placeholder-api";

interface DeleteStudySetDialogProps {
  id: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const DeleteStudySetDialog = ({
  id,
  open,
  onOpenChange,
}: DeleteStudySetDialogProps) => {
  const router = useRouter();
  const { mutate, isPending } = api.studySet.delete.useMutation({
    onSuccess() {
      toast({ title: "Successfully deleted study set" });
      router.push("/latest");
    },
    onError() {
      toast({ title: "Couldn't delete study set, try again", variant: "destructive" });
    },
  });

  const deleteStudySet = () => {
    mutate({ id });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Are you absolutely sure?</DialogTitle>
          <DialogDescription>
            This action cannot be undone. This will permanently delete your
            study set and remove your data from our servers.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild disabled={isPending}>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button
            disabled={isPending}
            onClick={deleteStudySet}
            variant="destructive"
          >
            {isPending ? (
              <Loader2Icon size={16} className="animate-spin" />
            ) : (
              <>
                Delete <Trash2Icon size={16} className="ml-2" />
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default DeleteStudySetDialog;
