// src/app/(apps)/revision/layout.tsx
// src/app/layout.tsx
import { Inter } from 'next/font/google';
import QueryProvider from '@/providers/QueryProvider';
import { Toaster } from '@/components/ui/toaster';
import 'tailwindcss/tailwind.css';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryProvider>
          {children}
          <Toaster />
        </QueryProvider>
      </body>
    </html>
  );
}