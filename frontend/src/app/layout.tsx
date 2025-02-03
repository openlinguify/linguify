// src/app/layout.tsx
import type { Metadata } from "next";
import { UserProvider } from '@auth0/nextjs-auth0/client';
import { AuthProvider } from "@/providers/AuthProvider";
import { Toaster } from "@/components/ui/toaster";
import "@/styles/globals.css";
import { ThemeProvider } from "next-themes";

export const metadata: Metadata = {
  title: "Linguify - Learn Languages Easily",
  description: "Language learning platform for everyone.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-white dark:bg-gray-900">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem={true} disableTransitionOnChange> 
        <UserProvider>
          <AuthProvider>
            <main className="flex min-h-screen flex-col">
              {children}
            </main>
            <Toaster />
          </AuthProvider>
        </UserProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}