// src/app/layout.tsx
import type { Metadata } from "next";
import { Toaster } from "@/components/ui/toaster";
import "@/styles/globals.css";
import { ThemeProvider } from "next-themes";
import { AuthProvider } from "../services/AuthProvider";
import { OnboardingProvider } from "@/components/onboarding/OnboardingProvider";

export const metadata: Metadata = {
  title: "Linguify",
  description: "Language learning platform for everyone."
  // ... other metadata
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-white dark:bg-gray-900">
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false} disableTransitionOnChange>
        <AuthProvider>
          <OnboardingProvider>
            <main className="flex min-h-screen flex-col">
              {children}
            </main>
            <Toaster />
            </OnboardingProvider>
          </AuthProvider>

        </ThemeProvider>
      </body>
    </html>
  );
}