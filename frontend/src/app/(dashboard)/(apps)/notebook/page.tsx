// src/app/(dashboard)/(apps)/notebook/page.tsx
"use client";

import NotebookWrapper from '@/addons/notebook/components/NotebookWrapper.minimal';

export default function NotebookPage() {
  return (
    // Utiliser tout l'espace disponible pour le notebook
    <div className="-mx-4 -mt-4 h-[calc(100vh-3rem)] overflow-hidden">
      <NotebookWrapper />
    </div>
  );
}