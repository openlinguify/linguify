// src/app/(dashboard)/_components/sidebar.tsx

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  BookOpen, 
  LayoutDashboard, 
  MessageCircle, 
  Settings,
  Star 
} from "lucide-react";
import { cn } from "@/lib/utils";

const routes = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    href: "/",
  },
  {
    label: "Learning",
    icon: BookOpen,
    href: "/learning",
  },
  {
    label: "Revision",
    icon: BookOpen,
    href: "/revision",
  },
  {
    label: "Chat",
    icon: MessageCircle,
    href: "/chat",
  },
  {
    label: "Community",
    icon: Star,
    href: "/community",
  },
  {
    label: "Notes",
    icon: Star,
    href: "/notebook",
  },
  {
    label: "Coaching",
    icon: Star,
    href: "/coaching",
  },
  {
    label: "Progress",
    icon: Star,
    href: "/progress",
  },
  {
    label: "Task",
    icon: Star,
    href: "/task",
  },
  {
    label: "Settings",
    icon: Settings,
    href: "/settings",
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex flex-col h-full bg-white dark:bg-[#0f172a] border-r border-gray-200 dark:border-gray-800">
      {/* Logo */}
      <div className="p-6">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
          Linguify
        </h1>
      </div>

      {/* Navigation */}
      <div className="flex-1 p-3 space-y-1">
        {routes.map((route) => (
          <Link
            key={route.href}
            href={route.href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 dark:text-gray-400 transition-all duration-200",
              "hover:text-gray-900 dark:hover:text-gray-100",
              "hover:bg-gray-100 dark:hover:bg-gray-800/50",
              pathname === route.href && "bg-sky-50 dark:bg-sky-900/20 text-sky-700 dark:text-sky-400"
            )}
          >
            <route.icon className={cn(
              "h-4 w-4",
              pathname === route.href 
                ? "text-sky-700 dark:text-sky-400" 
                : "text-gray-500 dark:text-gray-400"
            )} />
            {route.label}
          </Link>
        ))}
      </div>
    </div>
  );
}