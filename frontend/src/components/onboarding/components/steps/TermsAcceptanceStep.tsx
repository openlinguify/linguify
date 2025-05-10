'use client';

import React, { useState } from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { FileText, CornerRightDown, ExternalLink } from 'lucide-react';
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { OnboardingFormData } from '../../hooks/useOnboardingForm';

interface TermsAcceptanceStepProps {
  formData: OnboardingFormData & {
    termsAccepted?: boolean;
  };
  validationErrors: Record<string, string>;
  onChange: (field: string, value: any) => void;
}

export const TermsAcceptanceStep: React.FC<TermsAcceptanceStepProps> = ({
  formData,
  validationErrors,
  onChange,
}) => {
  const { t } = useTranslation();
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  // Direct handler for the checkbox
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log("Checkbox changed:", e.target.checked);
    onChange('termsAccepted', e.target.checked);
  };

  // Handler for accepting terms in the dialog
  const handleAcceptTerms = () => {
    console.log("Accepting terms from dialog");
    onChange('termsAccepted', true);
    setIsDialogOpen(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-3 mb-6">
        <FileText className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
        <h3 className="text-xl font-bold">{t('onboarding.steps.terms.title', {}, "Legal Terms")}</h3>
      </div>

      <Alert className="mb-6">
        <AlertTitle className="flex items-center">
          <FileText className="h-4 w-4 mr-2" />
          {t('onboarding.steps.terms.alertTitle', {}, "Important Information")}
        </AlertTitle>
        <AlertDescription>
          {t('onboarding.steps.terms.description', {}, "Please review and accept our terms and conditions before continuing.")}
        </AlertDescription>
      </Alert>

      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 space-y-4">
        <div className="flex items-start">
          <div className="flex-1 space-y-2">
            <h4 className="font-medium">
              {t('onboarding.steps.terms.reviewPrompt', {}, "Please review our terms")}
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {t('onboarding.steps.terms.instructions', {}, "Click on the checkbox below after reading our terms and conditions to proceed with your registration.")}
            </p>
          </div>
          <CornerRightDown className="h-6 w-6 text-gray-400 ml-4 animate-bounce" />
        </div>

        <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
          <div className="flex items-center space-x-2 mb-4">
            <input
              type="checkbox"
              id="terms-checkbox"
              checked={!!formData.termsAccepted}
              onChange={handleCheckboxChange}
              className="h-5 w-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            <div>
              <Label
                htmlFor="terms-checkbox"
                className="font-medium cursor-pointer"
              >
                {t('terms.acceptLabel', {}, "I have read and accept the terms and conditions")}
              </Label>
              <p
                className="text-sm text-gray-500 underline cursor-pointer"
                onClick={() => setIsDialogOpen(true)}
              >
                {t('terms.readFullTerms', {}, "Read full terms")}
              </p>
            </div>
          </div>
        </div>

        {validationErrors.termsAccepted && (
          <div className="text-sm text-red-500 mt-2">
            {validationErrors.termsAccepted}
          </div>
        )}
      </div>

      <div className="text-sm text-gray-500 dark:text-gray-400 mt-2">
        {t('onboarding.steps.terms.additionalNote', {}, "By accepting our terms, you also acknowledge our Privacy Policy and agree to receive important updates about our service.")}
      </div>

      {/* Terms and Conditions Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>{t('terms.title', {}, "Terms and Conditions")}</DialogTitle>
            <DialogDescription>
              {t('terms.disclaimer', {}, "Please read these terms carefully before proceeding.")}
            </DialogDescription>
          </DialogHeader>

          <div className="max-h-[60vh] overflow-y-auto py-4">
            <h3 className="font-bold mb-2">1. Introduction</h3>
            <p className="mb-4">
              Welcome to Linguify, a language learning platform. By using our service, you agree to these Terms and Conditions.
            </p>

            <h3 className="font-bold mb-2">2. User Accounts</h3>
            <p className="mb-4">
              You are responsible for maintaining the security of your account and password.
              The company cannot and will not be liable for any loss or damage from your failure to comply.
            </p>

            <h3 className="font-bold mb-2">3. Privacy Policy</h3>
            <p className="mb-4">
              Our Privacy Policy describes how we handle the information you provide to us when you use our services.
              You understand that through your use of the services you consent to the collection and use of this information.
            </p>

            <h3 className="font-bold mb-2">4. Content and Services</h3>
            <p className="mb-4">
              All content provided on Linguify is protected by copyright and intellectual property laws.
              The content is provided "as is" without warranties of any kind.
            </p>

            <h3 className="font-bold mb-2">5. Termination</h3>
            <p className="mb-4">
              We reserve the right to terminate accounts that violate our terms or for any other reason at our sole discretion.
            </p>
          </div>

          <DialogFooter>
            <div className="flex justify-between w-full">
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Close
              </Button>
              <Button onClick={handleAcceptTerms} className="bg-primary">
                Accept Terms
              </Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default TermsAcceptanceStep;