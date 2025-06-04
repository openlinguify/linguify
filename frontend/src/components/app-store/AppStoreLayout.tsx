// src/components/app-store/AppStoreLayout.tsx
'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { App } from '@/core/api/appManagerApi';
import { useAppManager } from '@/core/context/AppManagerContext';
import { Search, Settings, MoreHorizontal, Package } from 'lucide-react';
import * as LucideIcons from 'lucide-react';

interface AppStoreLayoutProps {
  className?: string;
}

const categories = [
  { id: 'all', name: 'Tous', count: 4 },
  { id: 'learning', name: 'Apprentissage', count: 1 },
  { id: 'productivity', name: 'Productivité', count: 2 },
  { id: 'communication', name: 'Communication', count: 1 },
];

function AppStoreCard({ app, isInstalled, onToggle, loading }: {
  app: App;
  isInstalled: boolean;
  onToggle: (appCode: string, enabled: boolean) => Promise<void>;
  loading: boolean;
}) {
  const IconComponent = (LucideIcons as any)[app.icon_name] || Package;

  return (
    <Card className="relative group hover:shadow-lg transition-all duration-200 border border-gray-200 dark:border-gray-700">
      {/* Three dots menu */}
      <Button
        variant="ghost"
        size="sm"
        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 h-6 w-6"
      >
        <MoreHorizontal className="h-4 w-4" />
      </Button>

      <CardHeader className="pb-3">
        <div className="flex items-start space-x-3">
          {/* App Icon */}
          <div 
            className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: app.color }}
          >
            <IconComponent className="w-6 h-6 text-white" />
          </div>
          
          {/* App Info */}
          <div className="flex-1 min-w-0">
            <CardTitle className="text-lg font-semibold leading-tight">
              {app.display_name}
            </CardTitle>
            <CardDescription className="text-sm text-gray-600 dark:text-gray-400 mt-1 overflow-hidden" style={{
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical'
            }}>
              {app.description}
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="flex items-center justify-between">
          <Button
            className={`px-6 py-2 text-sm font-medium rounded ${
              isInstalled 
                ? 'bg-red-600 hover:bg-red-700 text-white' 
                : 'bg-purple-600 hover:bg-purple-700 text-white'
            }`}
            onClick={() => onToggle(app.code, !isInstalled)}
            disabled={loading}
          >
            {loading ? (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Processing...</span>
              </div>
            ) : (
              isInstalled ? 'Désinstaller' : 'Installer'
            )}
          </Button>
          
          <Button variant="ghost" size="sm" className="text-purple-600 hover:text-purple-700">
            En savoir plus
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function CategorySidebar({ selectedCategory, onCategoryChange }: {
  selectedCategory: string;
  onCategoryChange: (categoryId: string) => void;
}) {
  return (
    <div className="w-64 bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 p-4">
      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
        <Input 
          placeholder="Rechercher..."
          className="pl-10 bg-white dark:bg-gray-800"
        />
      </div>

      {/* Applications Section */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-3">
          <Package className="w-4 h-4 text-gray-600" />
          <h3 className="font-semibold text-gray-900 dark:text-white">APPLICATIONS</h3>
        </div>
        
        <div className="space-y-1">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => onCategoryChange(category.id)}
              className={`w-full flex items-center justify-between px-3 py-2 text-sm rounded-md transition-colors ${
                selectedCategory === category.id
                  ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <span>{category.name}</span>
              <Badge variant="secondary" className="text-xs">
                {category.count}
              </Badge>
            </button>
          ))}
        </div>
      </div>

    </div>
  );
}

export function AppStoreLayout({ className }: AppStoreLayoutProps) {
  const { 
    availableApps, 
    enabledAppCodes, 
    loading, 
    error, 
    toggleApp 
  } = useAppManager();
  
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [toggleLoading, setToggleLoading] = useState<string | null>(null);

  const handleToggle = async (appCode: string, enabled: boolean) => {
    setToggleLoading(appCode);
    try {
      await toggleApp(appCode, enabled);
    } finally {
      setToggleLoading(null);
    }
  };

  const filteredApps = availableApps.filter(app => {
    if (selectedCategory === 'all') return true;
    // Add filtering logic based on categories
    return true;
  });

  if (loading) {
    return (
      <div className="flex h-screen">
        <div className="w-64 bg-gray-50 dark:bg-gray-900 border-r"></div>
        <div className="flex-1 p-6">
          <div className="animate-pulse space-y-4">
            {Array(6).fill(0).map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 dark:bg-gray-800 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex h-screen bg-white dark:bg-gray-950 ${className}`}>
      {/* Sidebar */}
      <CategorySidebar 
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
      />
      
      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-6">
          {/* Header */}
          <div className="mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Apps</h1>
                <p className="text-gray-600 dark:text-gray-400">
                  Gérez vos applications Linguify
                </p>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <span>1-{filteredApps.length} / {filteredApps.length}</span>
                <Button variant="ghost" size="sm">
                  <Settings className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Apps Grid */}
          {error ? (
            <div className="text-center p-8">
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredApps.map((app) => (
                <AppStoreCard
                  key={app.id}
                  app={app}
                  isInstalled={enabledAppCodes.includes(app.code)}
                  onToggle={handleToggle}
                  loading={toggleLoading === app.code}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}