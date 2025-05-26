// src/app/(landing)/layout.tsx
'use client';

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuthContext } from "@/core/auth/AuthProvider";
import { LanguageProvider } from "@/core/i18n/i18nProvider";
import { Navbar } from "./_components/Navbar";
import { Footer } from "./_components/Footer";
import { CookieBanner } from "@/components/cookies";

export default function LandingLayoutClient({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isLoading } = useAuthContext();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Si l'utilisateur est authentifié et sur /home, rediriger vers le dashboard
    if (user && !isLoading && pathname === '/home') {
      router.push("/");
    }
  }, [user, isLoading, router, pathname]);

  return (
    <LanguageProvider>
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-grow">{children}</main>
        <Footer />
        <CookieBanner />
      </div>
    </LanguageProvider>
  );
}