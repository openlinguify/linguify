// src/components/app-store/AppStoreLayoutImproved.tsx
'use client';

import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { App } from '@/core/api/appManagerApi';
import { useAppManager } from '@/core/context/AppManagerContext';
import { Search, MoreHorizontal, Package, CheckCircle, XCircle, Clock } from 'lucide-react';
import * as LucideIcons from 'lucide-react';

interface AppStoreLayoutProps {
  className?: string;
}

interface AppCardProps {
  app: App;
  isInstalled: boolean;
  onToggle: (appCode: string, enabled: boolean) => Promise<void>;
  loading: boolean;
}

// Improved category mapping based on app codes
const getCategoryFromAppCode = (appCode: string): string => {
  const categoryMap: Record<string, string> = {
    'learning': 'apprentissage',
    'memory': 'apprentissage', 
    'notes': 'productivite',
    'conversation_ai': 'communication'
  };
  return categoryMap[appCode] || 'autre';
};

function AppCard({ app, isInstalled, onToggle, loading }: AppCardProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const { toast } = useToast();
  const IconComponent = (LucideIcons as any)[app.icon_name] || Package;
  
  const handleToggle = async () => {
    setIsProcessing(true);
    
    try {
      await onToggle(app.code, !isInstalled);
      
      toast({
        title: isInstalled ? "Application désinstallée" : "Application installée",
        description: `${app.display_name} ${isInstalled ? 'a été désinstallée' : 'est maintenant disponible'}.`,
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: "Erreur",
        description: `Erreur lors de l'opération. Veuillez réessayer.`,
        variant: "destructive",
        duration: 3000,
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Card className="relative group hover:shadow-lg transition-all duration-300 border border-gray-200 dark:border-gray-700 flex flex-col h-full">
      {/* Status indicator */}
      <div className="absolute top-2 left-2 z-10">
        {isInstalled && (
          <Badge 
            variant="secondary" 
            className="text-xs bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
          >
            <CheckCircle className="w-3 h-3 mr-1" />
            Installée
          </Badge>
        )}
      </div>

      {/* Three dots menu */}
      <Button
        variant="ghost"
        size="sm"
        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 h-6 w-6"
      >
        <MoreHorizontal className="h-4 w-4" />
      </Button>

      <CardHeader className="pb-3 pt-8">
        <div className="flex items-start space-x-3">
          <div 
            className="w-12 h-12 rounded-lg flex items-center justify-center text-white relative"
            style={{ backgroundColor: app.color || '#6B7280' }}
          >
            <IconComponent className="w-6 h-6" />
          </div>
          
          <div className="flex-1 min-w-0">
            <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white line-clamp-1">
              {app.display_name}
            </CardTitle>
            <CardDescription className="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
              {app.description}
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0 flex-1 flex flex-col justify-end">
        <div className="space-y-2">
          {isInstalled ? (
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button
                  className="w-full px-4 py-2 text-sm font-medium rounded transition-all duration-300 bg-red-600 hover:bg-red-700 text-white transform hover:scale-105"
                  disabled={loading || isProcessing}
                >
                  {(loading || isProcessing) ? (
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Désinstallation...</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center space-x-2">
                      <XCircle className="w-4 h-4" />
                      <span>Désinstaller</span>
                    </div>
                  )}
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Désinstaller {app.display_name} ?</AlertDialogTitle>
                  <AlertDialogDescription asChild>
                    <div>
                      <p className="mb-3">Cette action désinstallera l'application de votre compte.</p>
                      <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-md">
                        <div className="flex items-center text-sm text-blue-700 dark:text-blue-300">
                          <Clock className="w-4 h-4 mr-2 flex-shrink-0" />
                          <span><strong>Important :</strong> Vos données seront conservées pendant 30 jours après la désinstallation et pourront être récupérées si vous réinstallez l'application.</span>
                        </div>
                      </div>
                    </div>
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Annuler</AlertDialogCancel>
                  <AlertDialogAction 
                    onClick={handleToggle}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    Désinstaller
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          ) : (
            <Button
              className="w-full px-4 py-2 text-sm font-medium rounded transition-all duration-300 bg-purple-600 hover:bg-purple-700 text-white transform hover:scale-105"
              onClick={handleToggle}
              disabled={loading || isProcessing}
            >
              {(loading || isProcessing) ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Installation...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center space-x-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>Installer</span>
                </div>
              )}
            </Button>
          )}
          
          <Button variant="ghost" size="sm" className="w-full text-purple-600 hover:text-purple-700 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-all duration-300 transform hover:scale-105">
            En savoir plus
          </Button>
        </div>
        
      </CardContent>
    </Card>
  );
}

function CategorySidebar({ 
  selectedCategory, 
  onCategoryChange, 
  searchQuery, 
  onSearchChange,
  availableApps 
}: {
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  availableApps: App[];
}) {
  // Calculate dynamic counts based on actual apps
  const categories = useMemo(() => {
    const counts = availableApps.reduce((acc, app) => {
      const category = getCategoryFromAppCode(app.code);
      acc[category] = (acc[category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return [
      { id: 'all', name: 'Tous', count: availableApps.length },
      { id: 'apprentissage', name: 'Apprentissage', count: counts.apprentissage || 0 },
      { id: 'productivite', name: 'Productivité', count: counts.productivite || 0 },
      { id: 'communication', name: 'Communication', count: counts.communication || 0 },
    ];
  }, [availableApps]);

  return (
    <div className="w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 p-6">
      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
        <Input 
          placeholder="Rechercher une application..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
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

export function AppStoreLayoutImproved({ className }: AppStoreLayoutProps) {
  const { 
    availableApps, 
    loading, 
    error, 
    toggleApp,
    isAppEnabled
  } = useAppManager();

  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Enhanced filtering logic
  const filteredApps = useMemo(() => {
    return availableApps.filter(app => {
      // Search filter
      const matchesSearch = searchQuery === '' || 
        app.display_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        app.description.toLowerCase().includes(searchQuery.toLowerCase());

      // Category filter
      const matchesCategory = selectedCategory === 'all' || 
        getCategoryFromAppCode(app.code) === selectedCategory;

      return matchesSearch && matchesCategory;
    });
  }, [availableApps, searchQuery, selectedCategory]);

  const handleToggleApp = async (appCode: string, enabled: boolean) => {
    try {
      const success = await toggleApp(appCode, enabled);
      if (!success) {
        throw new Error('Toggle failed');
      }
    } catch (error) {
      throw error; // Re-throw to be caught by AppCard
    }
  };

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-lg font-medium text-gray-900 dark:text-white">Erreur de chargement</p>
          <p className="text-gray-600 dark:text-gray-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex h-full bg-gray-50 dark:bg-gray-900 ${className}`}>
      <CategorySidebar
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        availableApps={availableApps}
      />
      
      <div className="flex-1 p-6 overflow-auto">
        <div className="w-full">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Magasin d&apos;applications
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Installez et gérez vos applications Linguify. 
              {filteredApps.length > 0 && (
                <span className="ml-1">
                  {filteredApps.length} application{filteredApps.length > 1 ? 's' : ''} 
                  {selectedCategory !== 'all' && ` dans ${selectedCategory}`}
                  {searchQuery && ` correspondant à "${searchQuery}"`}
                </span>
              )}
            </p>
          </div>

          {/* Loading state */}
          {loading && (
            <div className="flex items-center justify-center h-32">
              <div className="flex items-center space-x-2">
                <div className="w-6 h-6 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-gray-600 dark:text-gray-400">Chargement des applications...</span>
              </div>
            </div>
          )}

          {/* Apps grid */}
          {!loading && (
            <>
              {filteredApps.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">
                  {filteredApps.map((app) => (
                    <AppCard
                      key={app.id}
                      app={app}
                      isInstalled={isAppEnabled(app.code)}
                      onToggle={handleToggleApp}
                      loading={loading}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg font-medium text-gray-900 dark:text-white">
                    Aucune application trouvée
                  </p>
                  <p className="text-gray-600 dark:text-gray-400">
                    {searchQuery 
                      ? `Aucune application ne correspond à "${searchQuery}"`
                      : 'Aucune application disponible dans cette catégorie'
                    }
                  </p>
                  {searchQuery && (
                    <Button
                      variant="outline"
                      onClick={() => setSearchQuery('')}
                      className="mt-4"
                    >
                      Effacer la recherche
                    </Button>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default AppStoreLayoutImproved;