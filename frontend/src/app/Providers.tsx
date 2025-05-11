'use client';
// src/app/Providers.tsx
import React, { useEffect } from 'react';
import { ThemeProvider } from 'next-themes';
import { AuthProvider } from '@/core/auth/AuthProvider';
import { UserSettingsProvider } from '@/core/context/UserSettingsContext';
import { OnboardingProvider } from '@/components/onboarding/OnboardingProvider';
import { NotificationProvider } from '@/core/context/NotificationContext';
import QueryProvider from '@/core/providers/QueryProvider';
import { LanguageProvider } from '@/core/i18n/i18nProvider';
import { LanguageSyncProvider } from '@/core/i18n/LanguageSyncProvider';
import { LanguageTransition } from '@/core/i18n/LanguageTransition';
import { registerServiceWorker } from '@/core/api/serviceWorkerRegistration';
import { Toaster } from '@/components/ui/toaster';

interface ProvidersProps {
  children: React.ReactNode;
}

function ServiceWorkerRegistration() {
  useEffect(() => {
    registerServiceWorker();
  }, []);
  
  return null;
}

export default function Providers({ children }: ProvidersProps) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <QueryProvider>
        <LanguageProvider>
          <AuthProvider>
            <UserSettingsProvider>
              <LanguageSyncProvider>
                <NotificationProvider>
                  <OnboardingProvider>
                    <ServiceWorkerRegistration />
                    {children}
                    <Toaster />
                    <LanguageTransition />
                  </OnboardingProvider>
                </NotificationProvider>
              </LanguageSyncProvider>
            </UserSettingsProvider>
          </AuthProvider>
        </LanguageProvider>
      </QueryProvider>
    </ThemeProvider>
  );
}