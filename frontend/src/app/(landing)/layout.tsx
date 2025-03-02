import type { Metadata } from "next";
import { LanguageProvider } from "@/components/LanguageContext";
import { Navbar } from "./_components/Navbar";
import { Footer } from "./_components/Footer";
import { Inter } from "next/font/google";

// Définition de la police Inter avec un sous-ensemble latin
const inter = Inter({ 
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter"
});

export const metadata: Metadata = {
  title: "Linguify",
  description: "Apprenez des langues facilement et efficacement avec Linguify",
  keywords: ["apprentissage des langues", "linguistique", "éducation"],
  authors: [{ name: "Linguify Team" }],
  viewport: "width=device-width, initial-scale=1",
  icons: {
    icon: "/favicon.ico",
    apple: "/apple-icon.png",
  },
  themeColor: "#ffffff",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className={inter.variable}>
      <body className="min-h-screen flex flex-col bg-gray-50">
        <LanguageProvider>
          <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-grow">{children}</main>
            <Footer />
          </div>
        </LanguageProvider>
      </body>
    </html>
  );
}