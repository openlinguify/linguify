"use client";

import { Layout, Compass, BookOpen, Crown, BookMarked, Settings, BarChart } from "lucide-react";
import { SidebarItem } from "./sidebar-item";
import { SidebarSection } from "./sidebar-section";

const guestRoutes = [
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
];

const learningRoutes = [
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
];

const premiumRoutes = [
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
];

export const SidebarRoutes = () => {
  return (
    <div className="flex flex-col w-full space-y-6">
      <SidebarSection>
        {guestRoutes.map((route) => (
          <SidebarItem
            key={route.href}
            icon={route.icon}
            label={route.label}
            href={route.href}
          />
        ))}
      </SidebarSection>

      <SidebarSection 
        label="Learning"
        premiumRequired={false}
      >
        {learningRoutes.map((route) => (
          <SidebarItem
            key={route.href}
            icon={route.icon}
            label={route.label}
            href={route.href}
          />
        ))}
      </SidebarSection>

      <SidebarSection
        label="Premium"
        premiumRequired={true}
      >
        {premiumRoutes.map((route) => (
          <SidebarItem
            key={route.href}
            icon={route.icon}
            label={route.label}
            href={route.href}
          />
        ))}
      </SidebarSection>
    </div>
  );
}