"use client";

import React from "react";
import { Sidebar } from "./_components/sidebar";
import { UserButton } from "@/components/ui/user-button";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";

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
          className="fixed inset-0 bg-black/30 z-40 md:hidden"
          onClick={() => setIsMobileSidebarOpen(false)}
        />
      )}

      {/* Sidebar Section */}
      <aside
        className={`
        fixed inset-y-0 z-50 
        flex h-full w-56 flex-col 
        bg-gray-100 border-r shadow-sm
        transition-transform duration-300
        md:translate-x-0 md:flex
        ${isMobileSidebarOpen ? "translate-x-0" : "-translate-x-full"}
      `}
      >
        <Sidebar />
      </aside>

      {/* Main Content Section */}
      <div className="flex-1 flex flex-col md:ml-56">
        {/* Top Header */}
        <header className="h-16 border-b bg-white flex items-center justify-between px-6 sticky top-0 z-30">
          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsMobileSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>

          {/* User Button */}
          <div className="ml-auto">
            <UserButton />
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 p-6 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
