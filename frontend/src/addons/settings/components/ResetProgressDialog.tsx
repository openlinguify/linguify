import React, { useState } from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";

interface ResetProgressDialogProps {
  onConfirmReset: () => Promise<void>;
  isResetting: boolean;
}

export function ResetProgressDialog({
  onConfirmReset,
  isResetting,
}: ResetProgressDialogProps) {
  const [open, setOpen] = useState(false);
  const [confirmText, setConfirmText] = useState("");
  const isConfirmValid = confirmText.toLowerCase() === "reset";

  const handleReset = async () => {
    await onConfirmReset();
    setOpen(false);
    setConfirmText("");
  };

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger asChild>
        <Button variant="outline" className="text-red-500">
          Réinitialiser la progression
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Réinitialiser toute la progression ?</AlertDialogTitle>
          <AlertDialogDescription className="space-y-4">
            Cette action va réinitialiser votre progression d'apprentissage pour la langue que vous étudiez actuellement,
            y compris les leçons complétées, scores, et statistiques associées. C'est comme si vous recommenciez à zéro avec cette langue.
            
            <span className="block font-semibold">
              Cette action est irréversible. Toutes vos données de progression pour cette langue seront définitivement supprimées.
            </span>
          </AlertDialogDescription>
        </AlertDialogHeader>
        
        <div className="py-3">
          <h4 className="text-sm font-medium mb-2">
            Pour confirmer, veuillez écrire "reset" ci-dessous :
          </h4>
          <Input
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            placeholder="reset"
            className="mb-2"
          />
        </div>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isResetting}>Annuler</AlertDialogCancel>
          <AlertDialogAction
            onClick={(e) => {
              e.preventDefault();
              handleReset();
            }}
            disabled={!isConfirmValid || isResetting}
            className="bg-red-500 hover:bg-red-600 text-white"
          >
            {isResetting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Réinitialisation...
              </>
            ) : (
              "Réinitialiser définitivement"
            )}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}