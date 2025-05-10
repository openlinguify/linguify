'use client';

import React from 'react';
import { useTranslation } from '@/core/i18n/useTranslations';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { RefreshCw } from 'lucide-react';
import { OnboardingFormData, ApiRequest } from '../hooks/useOnboardingForm';

interface OnboardingDevToolsProps {
  formData: OnboardingFormData;
  lastServerResponse: any;
  apiRequests: ApiRequest[];
  user: any;
  onRefreshData: () => void;
  onClearLog: () => void;
}

export const OnboardingDevTools: React.FC<OnboardingDevToolsProps> = ({
  formData,
  lastServerResponse,
  apiRequests,
  user,
  onRefreshData,
  onClearLog,
}) => {
  const { t } = useTranslation();

  return (
    <div className="bg-gray-100 dark:bg-gray-800 p-4 text-xs font-mono border-b border-gray-200 dark:border-gray-700 max-h-[150px] overflow-auto">
      <Accordion type="single" collapsible className="w-full">
        <AccordionItem value="form-data">
          <AccordionTrigger className="text-sm font-medium">
            {t('onboarding.devTools.sections.formData', {}, "Form Data")}
          </AccordionTrigger>
          <AccordionContent>
            <pre className="overflow-auto max-h-32 text-xs">
              {JSON.stringify(formData, null, 2)}
            </pre>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="server-response">
          <AccordionTrigger className="text-sm font-medium">
            {t('onboarding.devTools.sections.serverResponse', {}, "Last Server Response")}
          </AccordionTrigger>
          <AccordionContent>
            {lastServerResponse ? (
              <pre className="overflow-auto max-h-32 text-xs">
                {JSON.stringify(lastServerResponse, null, 2)}
              </pre>
            ) : (
              <div className="text-gray-500">{t('onboarding.devTools.noData.response', {}, "No response received yet")}</div>
            )}
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="user-data">
          <AccordionTrigger className="text-sm font-medium">
            {t('onboarding.devTools.sections.userData', {}, "Current User Data")}
          </AccordionTrigger>
          <AccordionContent>
            {user ? (
              <pre className="overflow-auto max-h-32 text-xs">
                {JSON.stringify(user, null, 2)}
              </pre>
            ) : (
              <div className="text-gray-500">{t('onboarding.devTools.noData.user', {}, "No user data available")}</div>
            )}
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="api-requests">
          <AccordionTrigger className="text-sm font-medium">
            {t('onboarding.devTools.sections.apiLog', {}, "API Requests Log")}
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-1">
              {apiRequests.length > 0 ? (
                apiRequests.map((req, index) => (
                  <div key={index} className="flex items-center gap-2 text-xs">
                    <span className="text-gray-500">{new Date(req.timestamp).toLocaleTimeString()}</span>
                    <Badge variant={req.status === 'error' ? 'destructive' :
                      (req.status === 'success' ? 'default' : 'outline')}>
                      {req.method}
                    </Badge>
                    <span>{req.endpoint}</span>
                    {req.status && (
                      <Badge variant={req.status === 'error' ? 'destructive' :
                        (req.status === 'success' ? 'default' : 'outline')}
                        className="ml-auto">
                        {req.status}
                      </Badge>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-gray-500">{t('onboarding.devTools.noData.api', {}, "No API requests logged")}</div>
              )}
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      <div className="flex gap-2 mt-2">
        <Button
          size="sm"
          variant="outline"
          className="h-8 text-xs"
          onClick={onRefreshData}
        >
          <RefreshCw className="h-3 w-3 mr-1" /> {t('onboarding.devTools.actions.refreshData', {}, "Refresh Server Data")}
        </Button>

        <Button
          size="sm"
          variant="outline"
          className="h-8 text-xs ml-auto"
          onClick={onClearLog}
        >
          {t('onboarding.devTools.actions.clearLog', {}, "Clear Log")}
        </Button>
      </div>
    </div>
  );
};

export default OnboardingDevTools;