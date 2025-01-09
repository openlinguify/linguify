"use client";

import React, { useState } from "react";
import { Badge } from "@/shared/components/ui/badge";
import {
  Layout,
  Compass,
  BookOpen,
  Crown,
  BookMarked,
  Settings,
  BarChart,
  Star,
  Cog
} from "lucide-react";

// Define routes configuration
const routes: Record<string, RouteSection> = {
  guest: {
    routes: [
      {
        icon: Layout,
        label: "Dashboard",
        href: "/",
      },
      {
        icon: Compass,
        label: "Browse",
        href: "/search",
        badge: "New",
      },
    ],
  },
  learning: {
    label: "Learning",
    premiumRequired: false,
    routes: [
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
      {
        icon: Star,
        label: "Achievements",
        href: "/achievements",
        badge: "Beta",
      },
    ],
  },
  settings: {
    routes: [
      {
        icon: Settings,
        label: "Settings",
        href: "/settings",
      }
    ],
  },
  premium: {
    label: "Premium",
    premiumRequired: true,
    routes: [
      {
        icon: Crown,
        label: "Premium Content",
        href: "/premium",
      },
    ],
  },
};

interface RouteItem {
  icon: any;
  label: string;
  href: string;
  badge?: string;
  disabled?: boolean;
  external?: boolean;
}

interface RouteSection {
  label?: string;
  routes: RouteItem[];
  premiumRequired?: boolean;
}

interface SidebarRoutesProps {
  className?: string;
  isPremium?: boolean;
}

// Simple utility to combine classes
const combineClasses = (...inputs: (string | undefined)[]) => {
  return inputs.filter(Boolean).join(" ");
};

// SidebarItem Component
const SidebarItem = ({
  icon: Icon,
  label,
  href,
  badge,
  active = false,
  external = false,
}: RouteItem & { active?: boolean }) => {
  const handleClick = () => {
    if (external) {
      window.open(href, '_blank');
    } else {
      window.location.href = href;
    }
  };

  return (
    <button
      onClick={handleClick}
      className={combineClasses(
        "flex items-center w-full p-3 rounded-lg transition-colors",
        active ? "bg-sky-100 text-sky-700" : "text-gray-600 hover:bg-gray-100"
      )}
    >
      <Icon className="h-5 w-5 mr-3 flex-shrink-0" />
      <span className="flex-1 text-left">{label}</span>
      {badge && (
        <Badge variant="secondary" className="ml-auto">
          {badge}
        </Badge>
      )}
    </button>
  );
};

// SidebarSection Component
const SidebarSection = ({
  label,
  children,
  premiumRequired = false,
}: {
  label?: string;
  children: React.ReactNode;
  premiumRequired?: boolean;
}) => (
  <div className="space-y-2">
    {label && (
      <div className="flex items-center px-3 py-2">
        <span className={combineClasses(
          "text-sm font-medium",
          premiumRequired ? "text-amber-700" : "text-gray-500"
        )}>
          {label}
        </span>
        {premiumRequired && (
          <Crown className="ml-2 h-4 w-4 text-amber-700" />
        )}
      </div>
    )}
    <div className="space-y-1">
      {children}
    </div>
  </div>
);

export const SidebarRoutes = ({ 
  className,
  isPremium = false 
}: SidebarRoutesProps) => {
  const [currentPath] = useState(typeof window !== 'undefined' ? window.location.pathname : '/');

  const isRouteActive = (href: string) => {
    return currentPath === href || currentPath.startsWith(`${href}/`);
  };

  const renderRouteItem = (route: RouteItem) => {
    if (route.disabled) {
      return null;
    }

    return (
      <SidebarItem
        key={route.href}
        {...route}
        active={isRouteActive(route.href)}
      />
    );
  };

  const renderRouteSection = ([key, section]: [string, RouteSection]) => {
    if (section.premiumRequired && !isPremium) {
      return null;
    }

    return (
      <SidebarSection
        key={key}
        label={section.label}
        premiumRequired={section.premiumRequired}
      >
        {section.routes.map(renderRouteItem)}
      </SidebarSection>
    );
  };

  return (
    <div className={combineClasses("flex flex-col w-full space-y-6", className)}>
      {/* Main navigation sections */}
      {Object.entries(routes).map(renderRouteSection)}
      
      {/* Settings button (always visible at bottom) */}
      <div className="mt-auto border-t pt-4">
        <SidebarItem
          icon={Cog}
          label="Settings"
          href="/settings"
          active={isRouteActive('/settings')}
        />
      </div>
      
      {/* Premium banner */}
      {!isPremium && (
        <div className="px-3 py-4">
          <div className="bg-gradient-to-r from-sky-500/20 to-blue-500/20 rounded-lg p-4">
            <h4 className="font-semibold text-sm mb-2 text-sky-700">
              Upgrade to Premium
            </h4>
            <p className="text-xs text-muted-foreground mb-3">
              Get access to all premium features and content
            </p>
            <a 
              href="/premium"
              className="inline-flex items-center justify-center w-full bg-gradient-to-r from-sky-600 to-blue-600 text-white text-sm font-medium py-2 px-4 rounded-md hover:from-sky-700 hover:to-blue-700 transition-colors"
            >
              <Crown className="w-4 h-4 mr-2" />
              Upgrade Now
            </a>
          </div>
        </div>
      )}
    </div>
  );
};