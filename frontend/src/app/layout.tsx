import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";

// Importation et configuration des polices
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Métadonnées personnalisées
export const metadata: Metadata = {
  title: "Linguify - Learn Languages Easily",
  description: "A personalized language learning app designed for your growth.",
};

// Composant RootLayout
export default function RootLayout({
  children,
}: {
  children: React.ReactNode; // Correction des types
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body
          className={`${geistSans.variable} ${geistMono.variable} bg-gray-50 min-h-screen`}
        >
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}