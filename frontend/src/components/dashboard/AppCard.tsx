// src/components/dashboard/AppCard.tsx
'use client';

import React from 'react';
import Link from 'next/link';
import { App } from '@/core/api/appManagerApi';
import * as LucideIcons from 'lucide-react';

interface AppCardProps {
  app: App;
  onMouseEnter?: () => void;
  observerRef?: React.RefObject<IntersectionObserver | null>;
}

export function AppCard({ app, onMouseEnter, observerRef }: AppCardProps) {
  const cardRef = React.useRef<HTMLAnchorElement>(null);
  
  // Dynamically get the icon component
  const IconComponent = (LucideIcons as any)[app.icon_name] || LucideIcons.Package;

  // Register with intersection observer for prefetching
  React.useEffect(() => {
    const observer = observerRef?.current;
    const element = cardRef.current;
    
    if (observer && element) {
      element.dataset.routePath = app.route_path;
      observer.observe(element);
      
      return () => {
        observer.unobserve(element);
      };
    }
  }, [app.route_path, observerRef]);

  return (
    <Link
      ref={cardRef}
      href={app.route_path}
      className="w-full"
      prefetch={false} // We'll handle prefetch manually
      onMouseEnter={onMouseEnter}
    >
      <div className="flex flex-col items-center group">
        <div 
          className="w-full max-w-[100px] aspect-square rounded-xl flex items-center justify-center mb-2 transition-all duration-300 group-hover:transform group-hover:scale-105 shadow-lg hover:shadow-xl"
          style={{ 
            backgroundColor: app.color
          }}
        >
          <IconComponent className="w-14 h-14 text-white" />
        </div>
        <span className="text-center font-medium text-sm font-sans tracking-tight text-[#374151] dark:text-white transition-all duration-300">
          {app.display_name}
        </span>
      </div>
    </Link>
  );
}