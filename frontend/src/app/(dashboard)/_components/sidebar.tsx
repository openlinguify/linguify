// src/app/(dashboard)/_components/sidebar.tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen, // Learning
  LayoutDashboard, // Dashboard
  Settings, // Settings App
  Brain, // Flashcard App
  BarChart, // Progress App
  BookMarked, // Revision App
  NotebookPen, // Notebook App
} from "lucide-react";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAuthContext } from "@/services/AuthProvider";

// Grouper les routes pour une meilleure organisation
const routes = [
  {
    label: "Main",
    routes: [
      {
        label: "Dashboard",
        icon: LayoutDashboard,
        href: "/",
        description: "Overview of your learning progress",
      },
    ],
  },
  {
    label: "Learning",
    routes: [
      {
        label: "Learning",
        icon: BookOpen,
        href: "/learning",
        description: "Start your learning journey",
      },
      {
        label: "Revision",
        icon: BookMarked,
        href: "/revision",
        description: "Review your learned materials",
      },
      {
        label: "Flashcard",
        icon: Brain,
        href: "/flashcard",
        description: "Practice with flashcards",
      }
    ],
  },
  {
    label: "Tools",
    routes: [
      {
        label: "Notes",
        icon: NotebookPen,
        href: "/notebook",
        description: "Your learning notes",
      },
      {
        label: "Progress",
        icon: BarChart,
        href: "/progress",
        description: "Track your progress",
      },
    ],
  },
  {
    label: "Settings",
    routes: [
      {
        label: "Settings",
        icon: Settings,
        href: "/settings",
        description: "Customize your experience",
      },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, isAuthenticated } = useAuthContext();


  return (
    <div className="flex flex-col h-full">
      {/* Navigation */}
      <ScrollArea className="flex-1">
        <div className="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
          {routes.map((group) => (
            <div key={group.label} className="space-y-2">
              <h2 className="px-4 text-xs uppercase tracking-wider text-muted-foreground font-semibold">
                {group.label}
              </h2>
              {group.routes.map((route) => (
                <Link
                  key={route.href}
                  href={route.href}
                  className={cn(
                    "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
                    "hover:bg-muted",
                    pathname === route.href
                      ? "bg-muted text-primary"
                      : "text-muted-foreground hover:text-primary"
                  )}
                  title={route.description}
                >
                  <route.icon
                    className={cn(
                      "h-4 w-4 transition-colors",
                      pathname === route.href
                        ? "text-brand-purple"
                        : "text-muted-foreground group-hover:text-brand-purple"
                    )}
                  />
                  {route.label}
                </Link>
              ))}
            </div>
          ))}
        </div>
      </ScrollArea>
      {isAuthenticated && user ? (
        <div className="p-4 border-t border-border mt-auto">
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-muted transition-colors">
            <div className="w-8 h-8 rounded-full bg-muted-foreground/10">
              {user.picture && (
                <img 
                  src={user.picture} 
                  alt="Profile" 
                  className="w-full h-full rounded-full object-cover" 
                />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user.name || "User Name"}</p>
              <p className="text-xs text-muted-foreground truncate">
                {user.email || "user@email.com"}
              </p>
            </div>
            <button
              onClick={() => {
                // Nettoyage local
                localStorage.clear();
                
                // Erase all cookies
                document.cookie.split(";").forEach(function(c) {
                  document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
                });
                
                // Logout Auth0 configuration
                const auth0Domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN;
                const clientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID;
                const returnTo = encodeURIComponent('http://localhost:3000/home');
                
                // Redirection to Auth0 logout
                window.location.href = `https://${auth0Domain}/v2/logout?client_id=${clientId}&returnTo=${returnTo}`;
              }}
              className="p-2 text-xs text-red-500 hover:text-red-700 hover:bg-red-50 rounded"
            >
              Déconnexion
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}