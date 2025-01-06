// frontend/src/lib/routes.ts
import { Layout, Compass, BookOpen, Crown, BookMarked, Settings, BarChart } from "lucide-react";

export const ROUTES = {
  guest: [
    {
      icon: Layout,
      label: "Dashboard",
      href: "/",
    },
    {
      icon: Compass,
      label: "Browse",
      href: "/search",
    },
  ],
  learning: [
    {
      icon: BookOpen,
      label: "My Courses",
      href: "/courses",
    },
    {
      icon: BookMarked,
      label: "Saved Items",
      href: "/saved",
    },
    {
      icon: BarChart,
      label: "Progress",
      href: "/progress",
    },
  ],
  premium: [
    {
      icon: Crown,
      label: "Premium Content",
      href: "/premium",
    },
    {
      icon: Settings,
      label: "Settings",
      href: "/settings",
    },
  ],
} as const;