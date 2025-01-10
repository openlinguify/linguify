// src/app/(dashboard)/layout.tsx
"use client";

import React from 'react';
import { Sidebar } from './_components/sidebar';
import { UserButton } from "@/shared/components/ui/user-button";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="h-full flex">
      {/* Sidebar Section */}
      <aside className="hidden md:flex h-full w-56 flex-col fixed inset-y-0 z-50 bg-gray-100 border-r shadow-sm">
        <Sidebar />
      </aside>

      {/* Main Content Section */}
      <div className="flex-1 flex flex-col md:ml-56">
        {/* Top Header */}
        <header className="h-16 border-b bg-white flex items-center justify-end px-6">
          <UserButton />
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}