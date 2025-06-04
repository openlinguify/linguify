// src/components/dashboard/AppCard.tsx
'use client';

import React from 'react';
import Link from 'next/link';
import { App } from '@/core/api/appManagerApi';
import * as LucideIcons from 'lucide-react';

interface AppCardProps {
  app: App;
  onMouseEnter?: () => void;
}

export function AppCard({ app, onMouseEnter }: AppCardProps) {
  // Dynamically get the icon component
  const IconComponent = (LucideIcons as any)[app.icon_name] || LucideIcons.Package;

  return (
    <Link
      href={app.route_path}
      className="w-full"
      prefetch={true}
      onMouseEnter={onMouseEnter}
    >
      <div className="flex flex-col items-center group">
        <div 
          className="w-full max-w-[100px] aspect-square rounded-xl flex items-center justify-center mb-2 transition-all duration-300 group-hover:transform group-hover:scale-105 shadow-lg hover:shadow-xl"
          style={{ 
            backgroundColor: app.color,
            ':hover': { 
              backgroundColor: `${app.color}E6` // Add some transparency on hover
            }
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