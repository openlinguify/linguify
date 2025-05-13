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
import { useTranslation } from '@/core/i18n/useTranslations';

interface ResetProgressDialogProps {
  onConfirmReset: () => Promise<void>;
  isResetting: boolean;
}

export function ResetProgressDialog({
  onConfirmReset,
  isResetting,
}: ResetProgressDialogProps) {
  const { t } = useTranslation();
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
          {typeof t('dangerZone.resetProgressButton') === 'string' ? t('dangerZone.resetProgressButton') : 'Reset Learning Progress'}
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{t('dangerZone.resetProgress.title')}</AlertDialogTitle>
          <AlertDialogDescription className="space-y-4">
            {t('dangerZone.resetProgress.description')}
            
            <span className="block font-semibold">
              {typeof t('dangerZone.resetProgress.warning') === 'string' ? t('dangerZone.resetProgress.warning') : 'Warning: This action cannot be undone!'}
            </span>
          </AlertDialogDescription>
        </AlertDialogHeader>
        
        <div className="py-3">
          <h4 className="text-sm font-medium mb-2">
            {typeof t('dangerZone.resetProgress.confirmPrompt') === 'string' ? t('dangerZone.resetProgress.confirmPrompt') : 'Type "reset" to confirm:'}
          </h4>
          <Input
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            placeholder="reset"
            className="mb-2"
          />
        </div>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={isResetting}>{t('cancel')}</AlertDialogCancel>
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
                {typeof t('dangerZone.resetProgress.resetting') === 'string' ? t('dangerZone.resetProgress.resetting') : 'Resetting progress...'}
              </>
            ) : (
              typeof t('dangerZone.resetProgress.confirmReset') === 'string' ? t('dangerZone.resetProgress.confirmReset') : 'Reset Progress'
            )}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}