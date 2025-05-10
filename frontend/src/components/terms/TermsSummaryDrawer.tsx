'use client';

import React, { useState } from 'react';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Check, ChevronRight, Info } from 'lucide-react';
import TermsModal from './TermsModal';
import { getTranslations, AvailableLocale, TERMS_LAST_UPDATED, CURRENT_TERMS_VERSION } from './termsContent';
import { useTranslation } from '@/core/i18n/useTranslations';

interface TermsSummaryDrawerProps {
  children: React.ReactNode;
  showAcceptButton?: boolean;
  onAccept?: () => void;
  version?: string;
  locale?: AvailableLocale;
}

export default function TermsSummaryDrawer({
  children,
  showAcceptButton = false,
  onAccept,
  version = CURRENT_TERMS_VERSION,
  locale = 'fr'
}: TermsSummaryDrawerProps) {
  const [isTermsModalOpen, setIsTermsModalOpen] = useState(false);

  // Get translations for current locale
  const translations = getTranslations(locale);

  // Define type for key points
  interface KeyPoint {
    title: string;
    description: string;
    icon?: React.ReactNode;
  }

  // Get key points and add icons
  const keyPoints = translations.keyPoints.map((point: { title: string; description: string }) => ({
    ...point,
    icon: <Check className="h-5 w-5 text-green-500" />
  }));

  return (
    <>
      <Sheet>
        <SheetTrigger asChild>
          {children}
        </SheetTrigger>
        <SheetContent className="w-full sm:max-w-md">
          <SheetHeader>
            <SheetTitle>{translations.title} {version}</SheetTitle>
            <SheetDescription>
              {translations.summary}
            </SheetDescription>
          </SheetHeader>
          
          <div className="py-4">
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 flex items-start space-x-3 mb-6">
              <Info className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-amber-800">
                {translations.summaryDisclaimer}
              </div>
            </div>
            
            <ScrollArea className="h-[50vh] pr-4">
              <div className="space-y-4">
                {keyPoints.map((point: KeyPoint, index: number) => (
                  <div key={index} className="flex items-start space-x-3 p-3 border border-gray-100 rounded-lg bg-white">
                    <div className="flex-shrink-0 mt-0.5">
                      {point.icon}
                    </div>
                    <div>
                      <h3 className="font-medium text-sm">{point.title}</h3>
                      <p className="text-sm text-gray-600 mt-1">{point.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
            
            <div className="mt-6 flex flex-col space-y-3">
              <Button
                variant="outline"
                className="w-full justify-between"
                onClick={() => setIsTermsModalOpen(true)}
              >
                <span>{translations.readFullTerms}</span>
                <ChevronRight className="h-4 w-4" />
              </Button>
              
              {showAcceptButton && onAccept && (
                <Button className="w-full" onClick={onAccept}>
                  {translations.acceptButton}
                </Button>
              )}
            </div>
            
            <div className="mt-4 text-xs text-center text-gray-500">
              {translations.lastUpdate} {TERMS_LAST_UPDATED}
            </div>
          </div>
        </SheetContent>
      </Sheet>
      
      <TermsModal
        isOpen={isTermsModalOpen}
        onClose={() => setIsTermsModalOpen(false)}
        onAccept={onAccept || (() => setIsTermsModalOpen(false))}
        version={version}
        showAcceptance={!!onAccept}
        standalone={true}
        locale={locale}
      />
    </>
  );
}