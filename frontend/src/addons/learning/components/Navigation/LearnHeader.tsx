// src/addons/learning/components/Navigation/LearnHeader.tsx
'use client';
import React from "react";
import {
  Filter, LayoutGrid, LayoutList, BookOpen, FileText,
  Calculator, ArrowRightLeft, PencilLine, Infinity, Layers
} from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { LearnHeaderProps } from "@/addons/learning/types";


// Definition of content types with their icons
const CONTENT_TYPES = [
  { value: 'all', label: 'All Content Types', icon: <Filter className="h-4 w-4" /> },
  { value: 'vocabulary', label: 'Vocabulary', icon: <FileText className="h-4 w-4" /> },
  { value: 'vocabularylist', label: 'Vocabulary List', icon: <FileText className="h-4 w-4" /> },
  { value: 'theory', label: 'Theory', icon: <BookOpen className="h-4 w-4" /> },
  { value: 'grammar', label: 'Grammar', icon: <BookOpen className="h-4 w-4" /> },
  { value: 'numbers', label: 'Numbers', icon: <Calculator className="h-4 w-4" /> },
  { value: 'multiple_choice', label: 'Multiple Choice', icon: <BookOpen className="h-4 w-4" /> },
  { value: 'fill_blank', label: 'Fill in Blanks', icon: <PencilLine className="h-4 w-4" /> },
  { value: 'matching', label: 'Matching', icon: <Infinity className="h-4 w-4" /> },
  { value: 'reordering', label: 'Reordering', icon: <ArrowRightLeft className="h-4 w-4" /> },
  { value: 'speaking', label: 'Speaking', icon: <BookOpen className="h-4 w-4" /> }
];

// Get the full name of a language from its code
function getLanguageFullName(languageCode: string): string {
  const languageMap: Record<string, string> = {
    'en': 'English',
    'fr': 'French',
    'es': 'Spanish',
    'nl': 'Dutch',
  };
  
  // Normalize language code to lowercase
  const normalizedCode = languageCode?.toLowerCase() || '';
  
  // Return full name or code if not found
  return languageMap[normalizedCode] || languageCode || '';
}

export default function LearnHeader({
  levelFilter,
  onLevelFilterChange,
  availableLevels,
  contentTypeFilter,
  onContentTypeChange,
  viewMode,
  onViewModeChange,
  layout,
  onLayoutChange,
  isCompactView,
  onCompactViewChange,
  targetLanguage
}: LearnHeaderProps) {
  // Track selected content types for multi-select
  const [selectedTypes, setSelectedTypes] = React.useState<string[]>([contentTypeFilter]);
  
  // Update selected types when contentTypeFilter changes from parent
  React.useEffect(() => {
    setSelectedTypes([contentTypeFilter]);
  }, [contentTypeFilter]);
  
  // Handle content type selection
  const handleContentTypeChange = (value: string) => {
    // If "all" is selected, clear other selections
    if (value === "all") {
      setSelectedTypes(["all"]);
      onContentTypeChange("all");
      return;
    }

    // If we're currently on "all", and selecting something else, replace with the new selection
    let newSelection: string[];
    if (selectedTypes.includes("all")) {
      newSelection = [value];
    } else {
      // Toggle the selection
      newSelection = selectedTypes.includes(value)
        ? selectedTypes.filter(type => type !== value) // Remove if already selected
        : [...selectedTypes, value]; // Add if not selected
    }

    // If no type is selected, default back to "all"
    if (newSelection.length === 0) {
      newSelection = ["all"];
    }

    setSelectedTypes(newSelection);

    // Currently only support single filter value
    if (newSelection.length === 1) {
      onContentTypeChange(newSelection[0]);
    } else {
      // For multiple selections, use the first one
      onContentTypeChange(newSelection[0]);
    }
  };

  return (
    <div className="bg-transparent p-4 rounded-lg shadow-sm mb-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        {/* Left: Language and Level */}
        <div className="flex items-center gap-2">
          {targetLanguage && (
            <div className="flex items-center gap-2">
              <span className="font-bold text-purple-700 dark:text-purple-300">
                {getLanguageFullName(targetLanguage)}
              </span>
              <Badge className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-400 text-white">
                {targetLanguage.toUpperCase()}
              </Badge>
            </div>
          )}
        </div>
        
        {/* Center: Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Level filter */}
          {availableLevels.length > 0 && (
            <Select value={levelFilter} onValueChange={onLevelFilterChange}>
              <SelectTrigger className="w-[120px] h-9">
                <div className="flex items-center gap-1">
                  <Layers className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                  <SelectValue placeholder="Level" />
                </div>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Levels</SelectItem>
                {availableLevels.map(level => (
                  <SelectItem key={level} value={level}>Level {level}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          
          {/* Content type filter */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="h-9">
                <Filter className="h-4 w-4 mr-2 text-gray-500 dark:text-gray-400" />
                {contentTypeFilter === "all" 
                  ? "All Content Types"
                  : CONTENT_TYPES.find(t => t.value === contentTypeFilter)?.label || contentTypeFilter}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuGroup>
                {CONTENT_TYPES.map((type) => (
                  <DropdownMenuCheckboxItem
                    key={type.value}
                    checked={selectedTypes.includes(type.value)}
                    onCheckedChange={() => handleContentTypeChange(type.value)}
                  >
                    {type.icon}
                    <span className="ml-2">{type.label}</span>
                  </DropdownMenuCheckboxItem>
                ))}
              </DropdownMenuGroup>
            </DropdownMenuContent>
          </DropdownMenu>
          
          {/* View mode selector avec boutons bien définis */}
          <div className="flex gap-0 border rounded-md overflow-hidden">
            <Button
              variant={viewMode === "units" || viewMode === "hierarchical" ? "default" : "outline"}
              size="sm"
              className={`rounded-none h-9 px-3 ${viewMode === "units" || viewMode === "hierarchical" ? "bg-purple-600 dark:bg-purple-800" : ""}`}
              onClick={() => onViewModeChange("units")}
              title="Afficher les unités avec leurs leçons"
            >
              <Layers className="h-4 w-4 mr-1" />
              <span className="text-xs">Unités</span>
            </Button>
            <Button
              variant={viewMode === "lessons" ? "default" : "outline"}
              size="sm"
              className={`rounded-none h-9 px-3 ${viewMode === "lessons" ? "bg-purple-600 dark:bg-purple-800" : ""}`}
              onClick={() => onViewModeChange("lessons")}
              title="Afficher uniquement les leçons regroupées par niveau"
            >
              <BookOpen className="h-4 w-4 mr-1" />
              <span className="text-xs">Leçons</span>
            </Button>
          </div>
        </div>
        
        {/* Right: Layout controls */}
        <div className="flex items-center gap-2">
          {/* Compact view toggle */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600 dark:text-gray-300">Compact</span>
            <Switch
              checked={isCompactView}
              onCheckedChange={onCompactViewChange}
            />
          </div>
          
          {/* Layout switcher */}
          <div className="flex border rounded-md overflow-hidden">
            <Button
              variant={layout === "list" ? "default" : "ghost"}
              size="icon"
              onClick={() => onLayoutChange("list")}
              className={`rounded-none h-9 w-9 ${layout === "list" ? "bg-purple-600 dark:bg-purple-800" : ""}`}
              title="Affichage en liste"
            >
              <LayoutList className="h-4 w-4" />
            </Button>
            <Button
              variant={layout === "grid" ? "default" : "ghost"}
              size="icon"
              onClick={() => onLayoutChange("grid")}
              className={`rounded-none h-9 w-9 ${layout === "grid" ? "bg-purple-600 dark:bg-purple-800" : ""}`}
              title="Affichage en grille"
            >
              <LayoutGrid className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}