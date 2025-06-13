// src/app/(dashboard)/layout.tsx
"use client";

import React, { useEffect, useMemo } from "react";
import Header from "./_components/header";
import { usePathname } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAuthContext } from "@/core/auth/AuthAdapter";
import { useTranslation } from "@/core/i18n/useTranslations";
// Terms imports disabled to prevent infinite loading
// import { useTermsGuard } from "@/core/auth/termsGuard";
// import TermsAcceptance from "@/components/terms/TermsAcceptance";
// import TermsNotification from "@/components/notifications/TermsNotification";
import { getUnauthenticatedRedirect, logEnvironmentInfo } from "@/core/utils/environment";

// Pages qui nécessitent la pleine largeur sans scroll externe
const FULL_WIDTH_PAGES = ['/settings', '/app-store'];
const FULL_HEIGHT_PAGES = ['/learning'];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, login } = useAuthContext();
  const pathname = usePathname();
  const { t, isLoading: translationsLoading, locale } = useTranslation();
  
  // EMERGENCY: Check if we have any auth indicator
  const hasAuthCookie = React.useMemo(() => {
    if (typeof window === 'undefined') return false;
    const cookies = document.cookie;
    return cookies.includes('access_token') || 
           cookies.includes('auth_token') || 
           cookies.includes('session') ||
           cookies.includes('sb-');
  }, []);
  
  // Terms guard - protect access until terms are accepted
  // DISABLED: Terms system causing infinite loading
  // const { termsAccepted, showTermsDialog } = useTermsGuard();
  const termsAccepted = true; // Force bypass
  const showTermsDialog = false; // Never show dialog
  
  // State to bypass terms check if dialog fails to show
  const [bypassTerms, setBypassTerms] = React.useState(false);
  
  // Check if we should skip terms entirely (development mode or after fresh login)
  const skipTermsCheck = process.env.NODE_ENV === 'development' || 
    (typeof window !== 'undefined' && localStorage.getItem('supabase_login_success') === 'true');

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
      // Log environment info for debugging
      logEnvironmentInfo('Dashboard Layout');
      
      // Journaliser l'accès au dashboard sans authentification
      console.log("[Auth Flow] Unauthorized access attempt to dashboard", {
        path: pathname,
        isLoading,
        isAuthenticated,
        isPublicPage,
        timestamp: new Date().toISOString()
      });

      // Determine redirect destination based on environment
      const redirectDestination = getUnauthenticatedRedirect();
      
      if (redirectDestination === '/home') {
        console.log(`[Auth Flow] Redirecting to /home (production mode)`);
        window.location.href = '/home';
      } else {
        console.log(`[Auth Flow] Redirecting to login with returnTo=${pathname}`);
        login(pathname);
      }
    } else if (!isLoading && isAuthenticated) {
      console.log("[Auth Flow] User successfully entered dashboard", {
        path: pathname,
        timestamp: new Date().toISOString()
      });
    }
  }, [isAuthenticated, isLoading, pathname, login, t, titleMap, translationsLoading]);

  // FORCE: Never show loading spinner - always render dashboard
  // Le système d'auth fonctionne en arrière-plan

  // Terms checking completely disabled to prevent infinite loading

  return (
    <div className="h-screen flex flex-col relative overflow-hidden">
      {/* Background with overlay for light mode - Minimal Linguify branded background */}
      <div className="absolute inset-0 bg-[url('/static/background_light/light.jpg')] bg-cover bg-no-repeat bg-fixed dark:hidden"></div>
      {/* Background with overlay for dark mode - Minimal Linguify branded background */}
      <div className="absolute inset-0 bg-[url('/static/background_dark/new/linguify-dark-minimal.svg')] bg-cover bg-no-repeat bg-fixed hidden dark:block"></div>
      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        {/* Terms components disabled to prevent infinite loading */}

        <Header />
        {/* Main Content */}
        <main className="flex-1 dark:text-white bg-transparent overflow-hidden flex flex-col">
          {FULL_HEIGHT_PAGES.some(page => pathname.startsWith(page)) ? (
            // Pour les pages learning, utiliser toute la hauteur
            (<div className="flex-1 flex flex-col overflow-hidden">{children}</div>)
          ) : FULL_WIDTH_PAGES.some(page => pathname.startsWith(page)) ? (
            // Pour les pages settings et app-store, utiliser toute la largeur sans scroll externe
            (<div className="flex-1 flex flex-col overflow-hidden">
              <div className="pt-6 w-full bg-transparent h-full">{children}</div>
            </div>)
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