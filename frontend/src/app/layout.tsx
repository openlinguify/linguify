// src/app/layout.tsx
import type { Metadata } from "next";
import "@/styles/globals.css";
import Providers from "./Providers";

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
        <Providers>
          <main className="flex min-h-screen flex-col">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}