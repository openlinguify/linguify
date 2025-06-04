// src/components/app-store/AppStoreGrid.tsx
'use client';

import React, { useState } from 'react';
import { AppStoreCard } from './AppStoreCard';
import { useAppManager } from '@/core/context/AppManagerContext';
import { Loader2, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';

export function AppStoreGrid() {
  const { 
    availableApps, 
    enabledAppCodes, 
    loading, 
    error, 
    toggleApp, 
    refreshApps 
  } = useAppManager();
  
  const [toggleLoading, setToggleLoading] = useState<string | null>(null);
  const { toast } = useToast();

  const handleToggle = async (appCode: string, enabled: boolean) => {
    setToggleLoading(appCode);
    
    try {
      const success = await toggleApp(appCode, enabled);
      
      if (success) {
        toast({
          title: enabled ? 'App Enabled' : 'App Disabled',
          description: `${appCode} has been ${enabled ? 'enabled' : 'disabled'} successfully.`,
        });
      } else {
        toast({
          title: 'Error',
          description: 'Failed to toggle app. Please try again.',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'An unexpected error occurred.',
        variant: 'destructive',
      });
    } finally {
      setToggleLoading(null);
    }
  };

  const handleRefresh = async () => {
    await refreshApps();
    toast({
      title: 'Refreshed',
      description: 'App data has been refreshed.',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading apps...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-8">
        <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
        <Button onClick={handleRefresh} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      </div>
    );
  }

  if (availableApps.length === 0) {
    return (
      <div className="text-center p-8">
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          No apps available at the moment.
        </p>
        <Button onClick={handleRefresh} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">App Store</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Manage your Linguify applications. Enable or disable apps as needed.
          </p>
        </div>
        <Button onClick={handleRefresh} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {availableApps
          .sort((a, b) => a.order - b.order)
          .map((app) => (
            <AppStoreCard
              key={app.id}
              app={app}
              isEnabled={enabledAppCodes.includes(app.code)}
              onToggle={handleToggle}
              loading={toggleLoading === app.code}
            />
          ))}
      </div>

      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
        <h3 className="font-semibold mb-2">Summary</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {enabledAppCodes.length} of {availableApps.length} apps enabled
        </p>
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-500">
          Enabled apps: {enabledAppCodes.join(', ') || 'None'}
        </div>
      </div>
    </div>
  );
}