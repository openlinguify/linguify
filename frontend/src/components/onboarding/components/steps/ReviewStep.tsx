'use client';

import React from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { Settings, RefreshCw, Check, X } from 'lucide-react';
import {
  Alert,
  AlertDescription,
} from '@/components/ui/alert';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { OnboardingFormData } from '../../hooks/useOnboardingForm';
import { useLocalizedLanguages } from '@/core/utils/languageUtils';

interface ReviewStepProps {
  formData: OnboardingFormData;
  initialData: OnboardingFormData;
  changedFieldsCount: number;
  onRefreshData: () => void;
}

export const ReviewStep: React.FC<ReviewStepProps> = ({
  formData,
  initialData,
  changedFieldsCount,
  onRefreshData,
}) => {
  const { t } = useTranslation();
  const {
    getLanguageOptions,
    getLevelOptions,
    getObjectivesOptions,
    getInterfaceLanguageOptions,
    getLocalizedLabel
  } = useLocalizedLanguages();

  // Helper to get display value for a field (handles select options)
  const getDisplayValue = (field: keyof OnboardingFormData, value: any): React.ReactNode => {
    if (field === 'termsAccepted') {
      return value ? (
        <div className="flex items-center text-green-600">
          <Check className="h-4 w-4 mr-1" />
          {t('common.accepted', {}, "Accepted")}
        </div>
      ) : (
        <div className="flex items-center text-red-600">
          <X className="h-4 w-4 mr-1" />
          {t('common.notAccepted', {}, "Not accepted")}
        </div>
      );
    }

    if (!value) return t('common.notSet', {}, "Not set");

    if (field === 'native_language' || field === 'target_language') {
      return getLocalizedLabel(getLanguageOptions(), value as string);
    } else if (field === 'language_level') {
      return getLocalizedLabel(getLevelOptions(), value as string);
    } else if (field === 'objectives') {
      return getLocalizedLabel(getObjectivesOptions(), value as string);
    } else if (field === 'interface_language') {
      return getLocalizedLabel(getInterfaceLanguageOptions(), value as string);
    }

    return value;
  };

  // Helper to get field label for display
  const getFieldLabel = (field: keyof OnboardingFormData): string => {
    const labelMap: Record<string, string> = {
      first_name: t('onboarding.steps.personalInfo.fields.firstName.label', {}, "First Name"),
      last_name: t('onboarding.steps.personalInfo.fields.lastName.label', {}, "Last Name"),
      username: t('onboarding.steps.personalInfo.fields.username.label', {}, "Username"),
      bio: t('onboarding.steps.personalInfo.fields.bio.label', {}, "Bio"),
      native_language: t('onboarding.steps.languages.fields.nativeLanguage.label', {}, "Native Language"),
      target_language: t('onboarding.steps.languages.fields.targetLanguage.label', {}, "Target Language"),
      language_level: t('onboarding.steps.learningPreferences.fields.languageLevel.label', {}, "Language Level"),
      objectives: t('onboarding.steps.learningPreferences.fields.objectives.label', {}, "Learning Objectives"),
      interface_language: t('onboarding.steps.learningPreferences.fields.interfaceLanguage.label', {}, "Interface Language"),
      termsAccepted: t('terms.title', {}, "Terms and Conditions")
    };
    return labelMap[field as string] || field as string;
  };

  // Filter fields to display them in a logical order
  const orderedFields = [
    'first_name',
    'last_name',
    'username',
    'bio',
    'native_language',
    'target_language',
    'language_level',
    'objectives',
    'interface_language',
    'termsAccepted'
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-3 mb-2">
        <Settings className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
        <h3 className="text-lg font-bold">{t('onboarding.steps.review.title', {}, "Review your information")}</h3>
      </div>

      <Alert className="mb-2 py-2">
        <AlertDescription className="text-sm">
          {t('onboarding.steps.review.description', {}, "Please verify your information before finalizing your profile setup.")}
        </AlertDescription>
      </Alert>

      {/* Review table with scrollable content */}
      <div className="border rounded-md overflow-hidden">
        <div className="max-h-[250px] overflow-y-auto">
          <Table className="w-full">
            <TableHeader className="sticky top-0 bg-white dark:bg-gray-900 z-10">
              <TableRow>
                <TableHead className="w-1/4 py-2">
                  {t('onboarding.steps.review.table.field', {}, "Field")}
                </TableHead>
                <TableHead className="w-1/4 py-2">
                  {t('onboarding.steps.review.table.currentValue', {}, "Current Value")}
                </TableHead>
                <TableHead className="py-2">
                  {t('onboarding.steps.review.table.newValue', {}, "New Value")}
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {orderedFields.map((field) => {
                const currentValue = initialData[field as keyof OnboardingFormData];
                const newValue = formData[field as keyof OnboardingFormData];
                const hasChanged = currentValue !== newValue;

                return (
                  <TableRow key={field} className={hasChanged ? "bg-yellow-50 dark:bg-yellow-900/20" : ""}>
                    <TableCell className="font-medium py-1.5">{getFieldLabel(field as keyof OnboardingFormData)}</TableCell>
                    <TableCell className="py-1.5">{getDisplayValue(field as keyof OnboardingFormData, currentValue)}</TableCell>
                    <TableCell className={`py-1.5 ${hasChanged ? "font-medium text-blue-600 dark:text-blue-400" : ""}`}>
                      {getDisplayValue(field as keyof OnboardingFormData, newValue)}
                      {hasChanged && (
                        <Badge variant="outline" className="ml-2 py-0 h-5 bg-blue-50 dark:bg-blue-900/20">
                          {t('onboarding.steps.review.table.updated', {}, "Updated")}
                        </Badge>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm mt-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onRefreshData}
          className="flex items-center h-8"
        >
          <RefreshCw className="mr-1 h-3 w-3" />
          {t('onboarding.steps.review.refreshData', {}, "Refresh Current Data")}
        </Button>

        <div className="text-sm text-gray-500">
          {t('onboarding.steps.review.fieldsToUpdate', { count: changedFieldsCount.toString() }, `${changedFieldsCount} field(s) will be updated`)}
        </div>
      </div>
    </div>
  );
};

export default ReviewStep;