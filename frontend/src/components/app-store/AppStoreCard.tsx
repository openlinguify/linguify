// src/components/app-store/AppStoreCard.tsx
'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { App } from '@/core/api/appManagerApi';
import * as LucideIcons from 'lucide-react';

interface AppStoreCardProps {
  app: App;
  isEnabled: boolean;
  onToggle: (appCode: string, enabled: boolean) => Promise<void>;
  loading?: boolean;
}

export function AppStoreCard({ app, isEnabled, onToggle, loading = false }: AppStoreCardProps) {
  // Dynamically get the icon component
  const IconComponent = (LucideIcons as any)[app.icon_name] || LucideIcons.Package;

  const handleToggle = async (checked: boolean) => {
    await onToggle(app.code, checked);
  };

  return (
    <Card className={`transition-all duration-200 hover:shadow-md ${isEnabled ? 'ring-2 ring-blue-500/20' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div 
              className="p-2 rounded-lg"
              style={{ backgroundColor: `${app.color}20` }}
            >
              <IconComponent 
                className="h-6 w-6" 
                style={{ color: app.color }}
              />
            </div>
            <div>
              <CardTitle className="text-lg">{app.display_name}</CardTitle>
              <div className="flex items-center space-x-2 mt-1">
                <Badge 
                  variant={isEnabled ? 'default' : 'secondary'}
                  className="text-xs"
                >
                  {isEnabled ? 'Enabled' : 'Disabled'}
                </Badge>
              </div>
            </div>
          </div>
          <Switch
            checked={isEnabled}
            onCheckedChange={handleToggle}
            disabled={loading}
            className="data-[state=checked]:bg-blue-600"
          />
        </div>
      </CardHeader>
      <CardContent>
        <CardDescription className="text-sm text-gray-600 dark:text-gray-400">
          {app.description}
        </CardDescription>
        <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
          <span>Route: {app.route_path}</span>
          <span>Order: {app.order}</span>
        </div>
      </CardContent>
    </Card>
  );
}