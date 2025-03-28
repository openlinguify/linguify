// src/app/layout.tsx
import type { Metadata } from "next";
import { Toaster } from "@/components/ui/toaster";
import "@/styles/globals.css";
import { ThemeProvider } from "next-themes";
import { AuthProvider } from "../services/AuthProvider";
import { OnboardingProvider } from "@/components/onboarding/OnboardingProvider";

export const metadata: Metadata = {
  title: "Linguify",
  description: "Language learning platform for everyone.",
  icons: {
    icon: [
      { url: '/logo/logo2.svg', type: 'image/svg+xml' },
    ],
  }
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/logo/logo2.svg" type="image/svg+xml" />
      </head>
      <body className="bg-white dark:bg-black text-black dark:text-white">
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