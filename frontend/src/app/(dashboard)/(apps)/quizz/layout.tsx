
// src/app/(dashboard)/(apps)/quizz/layout.tsx
import QueryProvider from '@/core/providers/QueryProvider';
import { ReactNode } from 'react';

interface QuizzLayoutProps {
  children: ReactNode;
}

export default function QuizzLayout({ children }: QuizzLayoutProps) {
  return (
    <QueryProvider>
      <div className="h-full w-full flex flex-col">
        {children}
      </div>
    </QueryProvider>
  );
}
