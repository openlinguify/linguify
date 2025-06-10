// src/app/(dashboard)/(apps)/app-store/layout.tsx
import React from 'react';

export default function AppStoreLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="h-screen overflow-hidden">
      {children}
    </div>
  );
}