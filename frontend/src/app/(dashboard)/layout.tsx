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
    <div className="min-h-screen flex flex-col">
      {/* Header - Full width at the top */}
      <Header />

      {/* Main container - below header */}
      <div className="flex-1 flex">
        {/* Mobile Sidebar Overlay */}
        {isMobileSidebarOpen && (
          <div
            className="fixed inset-0 bg-black/20 dark:bg-black/40 z-40 md:hidden backdrop-blur-sm"
            onClick={() => setIsMobileSidebarOpen(false)}
          />
        )}

        {/* Fixed Sidebar */}
        <aside
          className={`
            fixed top-14 bottom-0 w-56
            bg-white dark:bg-[#0f172a]
            border-r border-gray-200 dark:border-gray-800
            transition-all duration-300 ease-in-out
            md:translate-x-0 
            ${isMobileSidebarOpen ? "translate-x-0" : "-translate-x-full"}
          `}
        >
          <div className="h-full overflow-y-auto">
            <Sidebar />
          </div>
        </aside>

        {/* Main Content - with left margin to account for sidebar */}
        <main className="flex-1 ml-0 md:ml-56 bg-purple-50 min-h-[calc(100vh-56px)]">
          <div className="p-6 w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}