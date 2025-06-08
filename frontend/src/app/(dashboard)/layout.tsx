// src/app/(dashboard)/layout.tsx
"use client";

import React, { useEffect, useMemo } from "react";
import Header from "./_components/header";
import { usePathname } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAuthContext } from "@/core/auth/AuthAdapter";
import { useTranslation } from "@/core/i18n/useTranslations";
import { useTermsGuard } from "@/core/auth/termsGuard";
import TermsAcceptance from "@/components/terms/TermsAcceptance";
import TermsNotification from "@/components/notifications/TermsNotification";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, login } = useAuthContext();
  const pathname = usePathname();
  const { t, isLoading: translationsLoading, locale } = useTranslation();
  
  // Terms guard - protect access until terms are accepted
  const { termsAccepted, showTermsDialog } = useTermsGuard();

  // Créer une map de correspondance entre les chemins et les clés de traduction
  const titleMap = useMemo(() => ({
    '/': "Linguify",
    '/flashcard': 'dashboard.layoutpathname.flashcard',
    '/notebook': 'dashboard.layoutpathname.notebook',
    '/settings': 'dashboard.layoutpathname.settings',
    '/learning': 'dashboard.layoutpathname.learning',
    '/progress': 'dashboard.layoutpathname.progress',
    '/language_ai': 'dashboard.conversationAICard.title',
    '/quizz': 'Quiz Interactif',
  }), []);

  useEffect(() => {
    // Fonction pour déterminer le titre de la page
    const getPageTitle = () => {
      // Pages publiques qui n'ont pas besoin de traduction pour le titre
      const publicPages = ["/home", "/login", "/register", "/callback"];
      if (publicPages.includes(pathname)) {
        return "Linguify";
      }

      // Trouver la correspondance de chemin la plus spécifique
      const matchingPath = Object.keys(titleMap).find(path =>
        path !== '/' ? pathname.startsWith(path) : pathname === '/'
      ) as keyof typeof titleMap | undefined;

      const titleKey = matchingPath ? titleMap[matchingPath] : "Linguify";

      // Si c'est une clé de traduction et que les traductions sont chargées, traduire
      if (titleKey !== "Linguify" && !translationsLoading) {
        try {
          const translatedTitle = t(titleKey);
          // Vérifier si la traduction est valide (pas une clé de traduction)
          if (translatedTitle && !translatedTitle.includes('dashboard.layoutpathname')) {
            return translatedTitle;
          }
        } catch (e) {
          console.warn(`Translation failed for key: ${titleKey}`);
        }
      }

      return titleKey;
    };

    // Définir le titre de la page
    document.title = getPageTitle();

    // Pages publiques pour la logique d'authentification
    const publicPages = ["/home", "/login", "/register", "/callback"];
    const isPublicPage = publicPages.includes(pathname);

    // Check if user comes from simple login
    const hasSimpleLogin = localStorage.getItem('supabase_login_success') === 'true';
    
    if (!isLoading && !isAuthenticated && !isPublicPage && !hasSimpleLogin) {
      // Journaliser l'accès au dashboard sans authentification
      console.log("[Auth Flow] Unauthorized access attempt to dashboard", {
        path: pathname,
        isLoading,
        isAuthenticated,
        isPublicPage,
        timestamp: new Date().toISOString()
      });

      // Rediriger vers la page de connexion en préservant l'URL de retour
      console.log(`[Auth Flow] Redirecting to login with returnTo=${pathname}`);
      login(pathname);
    } else if (!isLoading && isAuthenticated) {
      console.log("[Auth Flow] User successfully entered dashboard", {
        path: pathname,
        timestamp: new Date().toISOString()
      });
    }
  }, [isAuthenticated, isLoading, pathname, login, t, titleMap, translationsLoading]);

  // Afficher l'indicateur de chargement pendant la vérification d'authentification
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-10 w-10 animate-spin text-purple-600" />
      </div>
    );
  }

  // Block access if terms not accepted
  if (isAuthenticated && !termsAccepted && !showTermsDialog) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-10 w-10 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col relative overflow-hidden">
      {/* Background with overlay for light mode - Minimal Linguify branded background */}
      <div className="absolute inset-0 bg-[url('/static/background_light/new/linguify-light-minimal.svg')] bg-cover bg-no-repeat bg-fixed dark:hidden"></div>
      {/* Background with overlay for dark mode - Minimal Linguify branded background */}
      <div className="absolute inset-0 bg-[url('/static/background_dark/new/linguify-dark-minimal.svg')] bg-cover bg-no-repeat bg-fixed hidden dark:block"></div>
      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Terms notification */}
        <TermsNotification />
        
        {/* Terms acceptance dialog */}
        {showTermsDialog && <TermsAcceptance />}

        <Header />
        {/* Main Content */}
        <main className="flex-1 dark:text-white bg-transparent overflow-hidden flex flex-col">
          {pathname.startsWith('/learning') ? (
            // Pour les pages learning, utiliser toute la hauteur
            (<div className="flex-1 flex flex-col overflow-hidden">{children}</div>)
          ) : (
            // Pour les autres pages, padding normal avec scroll
            (<div className="overflow-y-auto">
              <div className="pt-6 px-8 pb-8 w-full max-w-7xl mx-auto bg-transparent">{children}</div>
            </div>)
          )}
        </main>
      </div>
    </div>
  );
}