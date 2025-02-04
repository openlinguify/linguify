// src/app/(dashboard)/layout.tsx
"use client";

import React from "react";
import { Sidebar } from "./_components/sidebar";
import Header from "./_components/header";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = React.useState(false);

  return (
    <div className="h-full relative">
      {/* Mobile Sidebar Overlay */}
      {isMobileSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/20 dark:bg-black/40 z-40 md:hidden backdrop-blur-sm"
          onClick={() => setIsMobileSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
            fixed inset-y-0 z-50 
            flex h-full w-56 flex-col 
            bg-white dark:bg-[#0f172a] // Couleur spécifique pour matcher votre design
            border-r border-gray-200 dark:border-gray-800
            transition-all duration-300 ease-in-out
            md:translate-x-0 md:flex
            ${isMobileSidebarOpen ? "translate-x-0" : "-translate-x-full"}
          `}
      >
        <Sidebar />
      </aside>

      {/* Main Content */}
      <div className="flex flex-col md:pl-56">
        <Header />
        <main className="flex-1 overflow-y-auto bg-gray-50 dark:bg-[#0f172a] min-h-screen">
          <div className="container mx-auto p-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
