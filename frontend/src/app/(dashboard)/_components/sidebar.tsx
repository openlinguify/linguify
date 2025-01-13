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
    label: "Progress",
    icon: Star,
    href: "/progress",
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
    <div className="flex flex-col h-full bg-white border-r">
      {/* Logo */}
      <div className="p-6">
        <h1 className="text-2xl font-bold text-sky-700">
          Linguify
        </h1>
      </div>

      {/* Navigation */}
      <div className="flex-1 p-3">
        {routes.map((route) => (
          <Link
            key={route.href}
            href={route.href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-colors hover:text-gray-900 hover:bg-gray-100",
              pathname === route.href && "bg-sky-50 text-sky-700"
            )}
          >
            <route.icon className="h-4 w-4" />
            {route.label}
          </Link>
        ))}
      </div>
    </div>
  );
}