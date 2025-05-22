// src/addons/learning/components/Navigation/LearnHeader.tsx
'use client';
import React, { useState, useRef, useEffect } from "react";
import {
  LayoutGrid, LayoutList,
  Search, X
} from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { LearnHeaderProps } from "@/addons/learning/types";

// Definition of content types
const CONTENT_TYPES = [
  { value: 'all', label: 'Tous les types' },
  { value: 'vocabulary', label: 'Vocabulary' },
  { value: 'grammar', label: 'Grammar' },
  { value: 'culture', label: 'Culture' },
  { value: 'professional', label: 'Professional' }
];


// Enhanced language information
function getLanguageFullName(languageCode: string): string {
  const languageMap: Record<string, { name: string; nativeName: string; flag: string }> = {
    'en': { name: 'English', nativeName: 'English', flag: '🇬🇧' },
    'fr': { name: 'French', nativeName: 'Français', flag: '🇫🇷' },
    'es': { name: 'Spanish', nativeName: 'Español', flag: '🇪🇸' },
    'nl': { name: 'Dutch', nativeName: 'Nederlands', flag: '🇳🇱' },
  };
  
  const normalizedCode = languageCode?.toLowerCase() || '';
  return languageMap[normalizedCode]?.name || languageCode || '';
}

export default function LearnHeader({
  levelFilter,
  onLevelFilterChange,
  availableLevels,
  contentTypeFilter,
  onContentTypeChange,
  searchQuery = "",
  onSearchChange,
  viewMode,
  onViewModeChange,
  layout,
  onLayoutChange,
  isCompactView,
  onCompactViewChange,
  targetLanguage
}: LearnHeaderProps) {
  // Enhanced state management
  const [selectedTypes, setSelectedTypes] = useState<string[]>([contentTypeFilter]);
  const [localSearchQuery, setLocalSearchQuery] = useState<string>(searchQuery);
  const [showSearch, setShowSearch] = useState<boolean>(false);
  const searchInputRef = useRef<HTMLInputElement>(null);
  
  // Update selected types when contentTypeFilter changes from parent
  useEffect(() => {
    setSelectedTypes([contentTypeFilter]);
  }, [contentTypeFilter]);
  
  // Sync local search query with parent prop
  useEffect(() => {
    setLocalSearchQuery(searchQuery);
  }, [searchQuery]);
  
  // Focus search input when search is shown
  useEffect(() => {
    if (showSearch && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [showSearch]);
  
  // Debounced search functionality with enhanced logic
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (onSearchChange) {
        onSearchChange(localSearchQuery);
      }
      if (localSearchQuery.trim()) {
        console.log('🔍 Recherche avancée:', {
          query: localSearchQuery,
          filters: {
            level: levelFilter,
            contentType: contentTypeFilter,
            viewMode: viewMode
          }
        });
      }
    }, 300);
    
    return () => clearTimeout(timeoutId);
  }, [localSearchQuery, levelFilter, contentTypeFilter, viewMode, onSearchChange]);

  // Enhanced content type selection logic
  
  // Clear all filters
  const clearAllFilters = () => {
    setLocalSearchQuery("");
    if (onSearchChange) onSearchChange("");
    setShowSearch(false);
    onLevelFilterChange("all");
    onContentTypeChange("all");
    setSelectedTypes(["all"]);
  };
  
  // Get selected type label for display
  const getSelectedTypeLabel = () => {
    const selectedType = CONTENT_TYPES.find(t => t.value === contentTypeFilter);
    return selectedType?.label || 'Type';
  };
  
  // Get active filters count
  const getActiveFiltersCount = () => {
    let count = 0;
    if (levelFilter !== "all") count++;
    if (contentTypeFilter !== "all") count++;
    if (localSearchQuery.trim()) count++;
    return count;
  };

  return (
    <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 shadow-sm">
      <div className="w-full px-4">
        {/* Barre d'actions compacte */}
        <div className="py-1.5 flex items-center justify-between gap-3">
          {/* Left: Target Language Display */}
          <div className="flex items-center">
            {targetLanguage && (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800">
                <span className="text-xs font-medium text-purple-700 dark:text-purple-300">
                  {getLanguageFullName(targetLanguage)}
                </span>
              </div>
            )}
          </div>
          
          {/* Center: Filters & Search */}
          <div className="flex-1 flex items-center justify-center gap-2">
          
            {/* Search Bar */}
            <div className="relative w-48">
              <Search className="absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400" size={14} />
              <Input
                value={localSearchQuery}
                onChange={(e) => setLocalSearchQuery(e.target.value)}
                placeholder="Rechercher..."
                className="pl-8 pr-7 py-1 text-xs h-7 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600"
              />
              {localSearchQuery && (
                <button
                  onClick={() => { setLocalSearchQuery(""); if (onSearchChange) onSearchChange(""); }}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X size={12} />
                </button>
              )}
            </div>
            
            {/* Level Filter */}
            {availableLevels.length > 0 && (
              <Select value={levelFilter} onValueChange={onLevelFilterChange}>
                <SelectTrigger className="w-28 h-7 text-xs bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600">
                  <SelectValue placeholder="Niveau" />
                </SelectTrigger>
                <SelectContent className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                  <SelectItem value="all" className="text-xs hover:bg-gray-100 dark:hover:bg-gray-700">
                    Tous niveaux
                  </SelectItem>
                  {availableLevels.map(level => (
                    <SelectItem key={level} value={level} className="text-xs hover:bg-gray-100 dark:hover:bg-gray-700">
                      Niveau {level}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
            
            {/* Content Type Filter */}
            <Select value={contentTypeFilter} onValueChange={onContentTypeChange}>
              <SelectTrigger className="w-32 h-7 text-xs bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
                {CONTENT_TYPES.map((type) => (
                  <SelectItem 
                    key={type.value} 
                    value={type.value}
                    className="text-xs hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {/* Right: View Controls */}
          <div className="flex items-center gap-2">
            {/* View Mode */}
            <div className="flex bg-gray-100 dark:bg-gray-800 rounded-md p-0.5">
              <button
                onClick={() => onViewModeChange("units")}
                className={`px-3 py-1 text-xs rounded transition-colors ${
                  viewMode === "units" || viewMode === "hierarchical"
                    ? "bg-white dark:bg-gray-700 text-purple-600 dark:text-purple-400 shadow-sm"
                    : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                }`}
              >
                Unités
              </button>
              <button
                onClick={() => onViewModeChange("lessons")}
                className={`px-3 py-1 text-xs rounded transition-colors ${
                  viewMode === "lessons"
                    ? "bg-white dark:bg-gray-700 text-purple-600 dark:text-purple-400 shadow-sm"
                    : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                }`}
              >
                Leçons
              </button>
            </div>
            
            {/* Layout Toggle */}
            <div className="flex border border-gray-300 dark:border-gray-600 rounded-md overflow-hidden">
              <button
                onClick={() => onLayoutChange("list")}
                className={`p-1.5 transition-colors ${
                  layout === "list"
                    ? "bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400"
                    : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
                title="Vue liste"
              >
                <LayoutList size={14} />
              </button>
              <button
                onClick={() => onLayoutChange("grid")}
                className={`p-1.5 transition-colors ${
                  layout === "grid"
                    ? "bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400"
                    : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
                title="Vue grille"
              >
                <LayoutGrid size={14} />
              </button>
            </div>
            
            {/* Compact View */}
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-gray-600 dark:text-gray-400">Compact</span>
              <Switch
                checked={isCompactView}
                onCheckedChange={onCompactViewChange}
                className="scale-75 data-[state=checked]:bg-purple-600"
              />
            </div>
          </div>
        </div>
        
        {/* Active Filters - Compact Display */}
        {getActiveFiltersCount() > 0 && (
          <div className="px-4 py-1 bg-purple-50 dark:bg-purple-900/20 border-t border-purple-100 dark:border-purple-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs">
                <span className="text-purple-700 dark:text-purple-300 font-medium">Filtres:</span>
                {localSearchQuery.trim() && (
                  <Badge variant="secondary" className="text-xs h-5">
                    {localSearchQuery}
                  </Badge>
                )}
                {levelFilter !== "all" && (
                  <Badge variant="secondary" className="text-xs h-5">
                    {levelFilter}
                  </Badge>
                )}
                {contentTypeFilter !== "all" && (
                  <Badge variant="secondary" className="text-xs h-5">
                    {getSelectedTypeLabel()}
                  </Badge>
                )}
              </div>
              <button
                onClick={clearAllFilters}
                className="text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300"
              >
                <X size={12} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}