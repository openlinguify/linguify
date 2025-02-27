import type { Metadata } from "next";
import { LanguageProvider } from "@/components/LanguageContext";
import { Navbar } from "./_components/Navbar";

export const metadata: Metadata = {
    title: "Linguify",
    description: "Landing page for Linguify",
  };

  export default function RootLayout({
    children,
  }: {
    children: React.ReactNode;
  }) {
    return (
      <html lang="fr">
        <body>
          <LanguageProvider>
            <Navbar />
            {children}
          </LanguageProvider>
        </body>
      </html>
    );
  }