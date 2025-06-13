// EMERGENCY LAYOUT - Forces immediate display without auth checks
"use client";

import React from "react";
import Header from "./_components/header";
import { usePathname } from "next/navigation";

const FULL_WIDTH_PAGES = ['/settings', '/app-store'];
const FULL_HEIGHT_PAGES = ['/learning'];

export default function EmergencyDashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  
  console.log('[EmergencyLayout] Rendering without auth checks');
  
  return (
    <div className="h-screen flex flex-col relative overflow-hidden">
      {/* Background with overlay for light mode */}
      <div className="absolute inset-0 bg-[url('/static/background_light/light.jpg')] bg-cover bg-no-repeat bg-fixed dark:hidden"></div>
      {/* Background with overlay for dark mode */}
      <div className="absolute inset-0 bg-[url('/static/background_dark/new/linguify-dark-minimal.svg')] bg-cover bg-no-repeat bg-fixed hidden dark:block"></div>
      
      {/* Content */}
      <div className="relative z-10 flex flex-col h-full">
        <Header />
        
        {/* Main Content */}
        <main className="flex-1 dark:text-white bg-transparent overflow-hidden flex flex-col">
          {FULL_HEIGHT_PAGES.some(page => pathname.startsWith(page)) ? (
            <div className="flex-1 flex flex-col overflow-hidden">{children}</div>
          ) : FULL_WIDTH_PAGES.some(page => pathname.startsWith(page)) ? (
            <div className="flex-1 flex flex-col overflow-hidden">
              <div className="pt-6 w-full bg-transparent h-full">{children}</div>
            </div>
          ) : (
            <div className="overflow-y-auto">
              <div className="pt-6 px-8 pb-8 w-full max-w-7xl mx-auto bg-transparent">{children}</div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}