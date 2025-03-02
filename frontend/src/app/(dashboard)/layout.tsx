// src/app/(dashboard)/layout.tsx
"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "./_components/sidebar";
import Header from "./_components/header";
import { useAuth } from "@/providers/AuthProvider";
import { useRouter, usePathname } from "next/navigation";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  useEffect(() => {
    console.log("Auth State:", { user, isLoading, pathname });
    if (!user && !isLoading && pathname === '/') {
      router.push("/home");
    }
  }, [user, isLoading, router, pathname]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-lg font-semibold">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <div className="flex flex-1">
        {isMobileSidebarOpen && (
          <div
            className="fixed inset-0 bg-black/20 dark:bg-black/40 z-40 md:hidden backdrop-blur-sm"
            onClick={() => setIsMobileSidebarOpen(false)}
          />
        )}

        <aside
          className={`fixed top-14 bottom-0 w-56 bg-white dark:bg-[#0f172a] border-r border-gray-200 dark:border-gray-800 transition-transform duration-300 ease-in-out md:translate-x-0 
            ${isMobileSidebarOpen ? "translate-x-0" : "-translate-x-full"}`}
        >
          <div className="h-full overflow-y-auto">
            <Sidebar />
          </div>
        </aside>

        <main className="flex-1 md:pl-56 bg-purple-50 min-h-[calc(100vh-56px)]">
          <div className="p-6 w-full">{children}</div>
        </main>
      </div>
    </div>
  );
}