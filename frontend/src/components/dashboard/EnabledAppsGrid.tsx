// src/components/dashboard/EnabledAppsGrid.tsx
'use client';

import React, { useCallback, useEffect, useRef } from 'react';
import { AppCard } from './AppCard';
import { useAppManager } from '@/core/context/AppManagerContext';
import { Store } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';

export function EnabledAppsGrid() {
  const { enabledApps, loading, error } = useAppManager();
  const router = useRouter();
  const prefetchedRoutes = useRef(new Set<string>());
  const observerRef = useRef<IntersectionObserver | null>(null);

  // Prefetch route when app card becomes visible
  useEffect(() => {
    if (!('IntersectionObserver' in window)) return;

    observerRef.current = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && entry.target instanceof HTMLElement) {
          const routePath = entry.target.dataset.routePath;
          if (routePath && !prefetchedRoutes.current.has(routePath)) {
            // Use Next.js router prefetch
            router.prefetch(routePath);
            prefetchedRoutes.current.add(routePath);
          }
        }
      });
    }, {
      rootMargin: '50px' // Start prefetching 50px before the element is visible
    });

    return () => {
      observerRef.current?.disconnect();
    };
  }, [router]);

  // Enhanced prefetch on hover with data preloading
  const prefetchDataForApp = useCallback((routePath: string) => {
    // Prefetch the route if not already done
    if (!prefetchedRoutes.current.has(routePath)) {
      router.prefetch(routePath);
      prefetchedRoutes.current.add(routePath);
    }

    // Preload critical data for specific apps
    if (routePath === '/learning') {
      // Use dynamic import to load the API module only when needed
      import('@/addons/learning/api/courseAPI').then(({ courseAPI }) => {
        // Cache the units data
        courseAPI.getUnits().catch(() => {
          // Silently fail - this is just a prefetch
        });
      }).catch(() => {
        // Module loading failed - ignore for prefetch
      });
    } else if (routePath === '/flashcard') {
      import('@/addons/flashcard/api/revisionAPI').then(({ revisionAPI }) => {
        revisionAPI.getDecks().catch(() => {});
      }).catch(() => {});
    }
  }, [router]);

  if (loading) {
    return (
      <div className="flex justify-center px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 md:gap-8 justify-items-center w-full max-w-7xl">
          {Array(4).fill(0).map((_, i) => (
            <div key={i} className="w-full flex flex-col items-center">
              <div className="w-full max-w-[100px] aspect-square bg-gray-200 dark:bg-gray-800 rounded-xl mb-2"></div>
              <div className="w-20 h-4 bg-gray-200 dark:bg-gray-800 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-8">
        <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
        <Button asChild variant="outline">
          <Link href="/app-store">
            <Store className="h-4 w-4 mr-2" />
            Go to App Store
          </Link>
        </Button>
      </div>
    );
  }

  // Always add settings and app store to the enabled apps
  const settingsApp = {
    id: -1,
    code: 'settings',
    display_name: 'Settings',
    description: 'Manage your account and preferences',
    icon_name: 'Settings',
    color: '#6B7280',
    route_path: '/settings',
    is_enabled: true,
    order: 100,
    created_at: '',
    updated_at: ''
  };

  const appStoreApp = {
    id: -2,
    code: 'app_store',
    display_name: 'App Store',
    description: 'Manage your applications',
    icon_name: 'Store',
    color: '#059669',
    route_path: '/app-store',
    is_enabled: true,
    order: 101,
    created_at: '',
    updated_at: ''
  };

  const allApps = [
    ...enabledApps.sort((a, b) => a.order - b.order),
    settingsApp,
    appStoreApp
  ];

  if (enabledApps.length === 0) {
    return (
      <div className="text-center p-8">
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          No apps are currently enabled.
        </p>
        <Button asChild>
          <Link href="/app-store">
            <Store className="h-4 w-4 mr-2" />
            Visit App Store
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="flex justify-center px-4 sm:px-6 lg:px-8">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6 md:gap-8 justify-items-center w-full max-w-7xl">
        {allApps.map((app) => (
          <AppCard
            key={app.id}
            app={app}
            onMouseEnter={() => prefetchDataForApp(app.route_path)}
            observerRef={observerRef}
          />
        ))}
      </div>
    </div>
  );
}