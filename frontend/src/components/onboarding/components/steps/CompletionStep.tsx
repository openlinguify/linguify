'use client';

import React from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { CheckCircle, ExternalLink } from 'lucide-react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Alert,
  AlertTitle,
  AlertDescription,
} from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { OnboardingFormData } from '../../hooks/useOnboardingForm';
import {
  LANGUAGE_OPTIONS,
  LEVEL_OPTIONS,
  OBJECTIVES_OPTIONS,
  INTERFACE_LANGUAGE_OPTIONS
} from '@/addons/settings/constants/usersettings';

interface CompletionStepProps {
  formData: OnboardingFormData;
  lastServerResponse: any;
  showDevTools: boolean;
  onToggleDevTools: () => void;
}

export const CompletionStep: React.FC<CompletionStepProps> = ({
  formData,
  lastServerResponse,
  showDevTools,
  onToggleDevTools,
}) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-4">
      <div className="flex flex-col items-center justify-center mb-4">
        <div className="bg-green-100 dark:bg-green-900/30 p-4 rounded-full">
          <CheckCircle className="h-12 w-12 text-green-600 dark:text-green-500" />
        </div>
        <h3 className="text-2xl font-bold mt-4">{t('onboarding.steps.completion.title', {}, "You're all set!")}</h3>
        <p className="text-gray-600 dark:text-gray-400 max-w-md text-center mt-2">
          {t('onboarding.steps.completion.description', {}, "Your profile has been configured. Now you can start your language learning journey with Linguify.")}
        </p>
      </div>

      <Card className="w-full max-w-md border-0 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 mx-auto">
        <CardHeader>
          <CardTitle className="text-lg text-left text-indigo-700 dark:text-indigo-400">
            {t('onboarding.steps.completion.learningPath.title', {}, "Your Learning Path")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3 text-left text-gray-700 dark:text-gray-300">
            <li className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-medium">{t('onboarding.steps.completion.learningPath.targetLanguage', {}, "Learning Language:")}</span>
                <p>{LANGUAGE_OPTIONS.find(l => l.value === formData.target_language)?.label || 'Unknown'}</p>
              </div>
            </li>
            <li className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-medium">{t('onboarding.steps.completion.learningPath.nativeLanguage', {}, "Native Language:")}</span>
                <p>{LANGUAGE_OPTIONS.find(l => l.value === formData.native_language)?.label || 'Unknown'}</p>
              </div>
            </li>
            <li className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-medium">{t('onboarding.steps.completion.learningPath.level', {}, "Current Level:")}</span>
                <p>{LEVEL_OPTIONS.find(l => l.value === formData.language_level)?.label || 'Beginner'}</p>
              </div>
            </li>
            <li className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-medium">{t('onboarding.steps.completion.learningPath.objectives', {}, "Learning Goals:")}</span>
                <p>{OBJECTIVES_OPTIONS.find(o => o.value === formData.objectives)?.label || 'General Learning'}</p>
              </div>
            </li>
            <li className="flex items-start">
              <CheckCircle className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-medium">{t('onboarding.steps.completion.learningPath.interfaceLanguage', {}, "Interface Language:")}</span>
                <p>{INTERFACE_LANGUAGE_OPTIONS.find(i => i.value === formData.interface_language)?.label || 'English'}</p>
              </div>
            </li>
          </ul>
        </CardContent>
      </Card>

      {lastServerResponse && (
        <Alert className="bg-green-50 dark:bg-green-900/20 border-green-200 w-full max-w-md mt-2 mx-auto">
          <AlertTitle className="flex items-center text-green-700 dark:text-green-400">
            <CheckCircle className="h-4 w-4 mr-2" />
            {t('onboarding.steps.completion.successMessage.title', {}, "Profile Successfully Updated")}
          </AlertTitle>
          <AlertDescription className="text-sm text-gray-700 dark:text-gray-300">
            <p>{t('onboarding.steps.completion.successMessage.timestamp', { timestamp: new Date().toLocaleString() }, `Your profile was updated on ${new Date().toLocaleString()}`)}</p>
            {showDevTools ? (
              <p className="text-xs text-gray-500 mt-1">Server response data available in developer tools</p>
            ) : (
              <Button
                variant="link"
                className="p-0 h-auto text-sm text-indigo-600 dark:text-indigo-400"
                onClick={onToggleDevTools}
              >
                <ExternalLink className="h-3 w-3 mr-1 inline" />
                {t('onboarding.steps.completion.successMessage.viewResponse', {}, "View server response")}
              </Button>
            )}
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default CompletionStep;