import React, { useState } from 'react';
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Loader2, Clock, AlertTriangle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { useTranslation } from '@/core/i18n/useTranslations';

interface DeleteAccountDialogProps {
  onConfirmTemporary: () => Promise<void>;
  onConfirmPermanent: () => Promise<void>;
  isDeleting: boolean;
}

export type DeletionType = 'temporary' | 'permanent';

export function DeleteAccountDialog({ 
  onConfirmTemporary, 
  onConfirmPermanent, 
  isDeleting 
}: DeleteAccountDialogProps) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  const [error, setError] = useState('');
  const [deletionType, setDeletionType] = useState<DeletionType>('temporary');

  const handleConfirmDelete = async () => {
    // Confirm text validation only for permanent deletion
    if (deletionType === 'permanent' && confirmText.toLowerCase() !== 'delete') {
      setError(typeof t('dangerZone.deleteAccount.confirmError') === 'string' ? t('dangerZone.deleteAccount.confirmError') : 'Please type "delete" to confirm');
      return;
    }
    
    setError('');
    
    try {
      // Call the appropriate handler based on deletion type
      if (deletionType === 'temporary') {
        await onConfirmTemporary();
      } else {
        await onConfirmPermanent();
      }
      
      setOpen(false); // Close dialog after successful deletion
    } catch (err) {
      // Error handling is managed by the parent component
      console.error("Error during account deletion:", err);
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger asChild>
        <Button 
          variant="destructive"
          disabled={isDeleting}
        >
          {isDeleting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {typeof t('dangerZone.deleting') === 'string' ? t('dangerZone.deleting') : 'Deleting...'}
            </>
          ) : (
            <>{typeof t('dangerZone.deleteAccountButton') === 'string' ? t('dangerZone.deleteAccountButton') : 'Delete Account'}</>
          )}
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent className="max-w-[500px]">
        <AlertDialogHeader>
          <AlertDialogTitle>{typeof t('dangerZone.deleteAccount.title') === 'string' ? t('dangerZone.deleteAccount.title') : 'Delete Your Account'}</AlertDialogTitle>
          <AlertDialogDescription>
            {typeof t('dangerZone.deleteAccount.choose') === 'string' ? t('dangerZone.deleteAccount.choose') : 'Choose a deletion option'}
          </AlertDialogDescription>
        </AlertDialogHeader>
        
        <div className="space-y-6 py-2">
          <RadioGroup value={deletionType} onValueChange={(value) => setDeletionType(value as DeletionType)}>
            <div className="space-y-4">
              <div className="flex items-start space-x-2">
                <RadioGroupItem value="temporary" id="option-temporary" />
                <div className="grid gap-1.5 leading-none">
                  <Label htmlFor="option-temporary" className="font-medium text-base">
                    {typeof t('dangerZone.deleteAccount.temporaryDeletion') === 'string' ? t('dangerZone.deleteAccount.temporaryDeletion') : 'Deactivate My Account (30-day recovery)'}
                  </Label>
                  <Card className="mt-2">
                    <CardContent className="p-3 flex gap-3 items-center">
                      <Clock className="h-5 w-5 text-amber-500 flex-shrink-0" />
                      <p className="text-sm text-muted-foreground">
                        {typeof t('dangerZone.deleteAccount.temporaryDescription') === 'string' ? t('dangerZone.deleteAccount.temporaryDescription') : 'Your account will be deactivated immediately and scheduled for permanent deletion after 30 days. You can recover your account by logging in during this period.'}
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>
              
              <div className="flex items-start space-x-2">
                <RadioGroupItem value="permanent" id="option-permanent" />
                <div className="grid gap-1.5 leading-none">
                  <Label htmlFor="option-permanent" className="font-medium text-base">
                    {typeof t('dangerZone.deleteAccount.permanentDeletion') === 'string' ? t('dangerZone.deleteAccount.permanentDeletion') : 'Delete My Account Permanently'}
                  </Label>
                  <Card className="mt-2">
                    <CardContent className="p-3 flex gap-3 items-center">
                      <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0" />
                      <p className="text-sm text-muted-foreground">
                        {typeof t('dangerZone.deleteAccount.permanentDescription') === 'string' ? t('dangerZone.deleteAccount.permanentDescription') : 'Your account will be permanently deleted immediately. All your data will be removed and this action cannot be undone.'}
                      </p>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          </RadioGroup>
          
          {deletionType === 'permanent' && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                {typeof t('dangerZone.deleteAccount.confirmPrompt') === 'string' ? t('dangerZone.deleteAccount.confirmPrompt') : 'To confirm permanent deletion, please type'} <span className="font-semibold">delete</span> {typeof t('dangerZone.deleteAccount.confirmPromptSuffix') === 'string' ? t('dangerZone.deleteAccount.confirmPromptSuffix') : 'below:'}
              </p>
              <Input
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                placeholder="delete"
                autoComplete="off"
                className={error ? "border-destructive" : ""}
              />
              {error && <p className="text-sm text-destructive">{error}</p>}
            </div>
          )}
        </div>
        
        <AlertDialogFooter>
          <AlertDialogCancel>{t('cancel')}</AlertDialogCancel>
          <AlertDialogAction 
            onClick={handleConfirmDelete} 
            className={deletionType === 'permanent' 
              ? "bg-destructive text-destructive-foreground hover:bg-destructive/90" 
              : ""}
          >
            {isDeleting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {typeof t('dangerZone.deleting') === 'string' ? t('dangerZone.deleting') : 'Deleting...'}
              </>
            ) : (
              <>{deletionType === 'temporary' ? 
                (typeof t('dangerZone.deleteAccount.deactivateAccount') === 'string' ? t('dangerZone.deleteAccount.deactivateAccount') : 'Deactivate My Account') : 
                (typeof t('dangerZone.deleteAccount.deletePermanently') === 'string' ? t('dangerZone.deleteAccount.deletePermanently') : 'Delete Permanently')
              }</>
            )}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}