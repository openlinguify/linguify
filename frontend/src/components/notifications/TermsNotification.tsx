'use client';

import React from 'react';
import { Bell, FileText, AlertTriangle } from 'lucide-react';
import { useTermsAcceptance } from '@/core/hooks/useTermsAcceptance';
import { TermsSummaryDrawer } from '@/components/terms';
import { Button } from '@/components/ui/button';
import { useTranslation } from '@/core/i18n/useTranslations';
import { AvailableLocale } from '@/components/terms/termsContent';

interface TermsNotificationProps {
  variant?: 'banner' | 'inline' | 'minimal';
  version?: string;
  locale?: AvailableLocale;
}

export default function TermsNotification({
  variant = 'banner',
  version = 'v1.0',
  locale = 'fr'
}: TermsNotificationProps) {
  const {
    termsAccepted,
    loading,
    handleTermsAccepted
  } = useTermsAcceptance();
  
  const { t } = useTranslation();

  // If terms already accepted or still loading, don't show anything
  if (termsAccepted || loading) {
    return null;
  }

  // Banner variant (full width notification at the top of the page)
  if (variant === 'banner') {
    return (
      <>
        <div className="w-full bg-primary/90 text-white py-3 px-4 flex items-center justify-between shadow-md backdrop-blur-sm sticky top-0 z-50">
          <div className="flex items-center space-x-3">
            <AlertTriangle size={18} className="text-amber-200" />
            <p className="text-sm font-medium">
              {t('termsNotification.banner.message')}
            </p>
          </div>
          <TermsSummaryDrawer showAcceptButton={true} onAccept={handleTermsAccepted} version={version} locale={locale}>
            <Button variant="secondary" size="sm" className="text-xs font-medium">
              {t('termsNotification.banner.button')}
            </Button>
          </TermsSummaryDrawer>
        </div>
      </>
    );
  }

  // Inline variant (component that can be placed anywhere)
  if (variant === 'inline') {
    return (
      <>
        <div className="w-full bg-slate-50 border border-slate-200 rounded-lg p-4 shadow-sm">
          <div className="flex items-start space-x-3">
            <FileText className="text-primary mt-0.5" size={18} />
            <div className="flex-1">
              <h4 className="font-medium text-slate-900">
                {t('termsNotification.inline.title')}
              </h4>
              <p className="text-sm text-slate-700 mt-1">
                {t('termsNotification.inline.message')}
              </p>
              <div className="mt-3 flex gap-2">
                <TermsSummaryDrawer showAcceptButton={true} onAccept={handleTermsAccepted} version={version} locale={locale}>
                  <Button size="sm" variant="default">
                    {t('termsNotification.inline.button')}
                  </Button>
                </TermsSummaryDrawer>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  }

  // Minimal variant (just an icon button)
  return (
    <>
      <TermsSummaryDrawer showAcceptButton={true} onAccept={handleTermsAccepted} version={version} locale={locale}>
        <button
          className="relative p-2 rounded-full bg-amber-50 text-amber-600 hover:bg-amber-100 transition-colors"
          aria-label={t('termsNotification.minimal.ariaLabel')}
        >
          <Bell size={18} />
          <span className="absolute top-0 right-0 block w-2 h-2 bg-amber-600 rounded-full"></span>
        </button>
      </TermsSummaryDrawer>
    </>
  );
}