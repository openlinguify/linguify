import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { 
  Filter, 
  Calendar,
  Languages,
  SortAsc,
  SortDesc,
  Clock,
  X
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Note } from "@/addons/notebook/types";

export type SortType = "title" | "updated" | "created" | "language";
export type SortDirection = "asc" | "desc";

export interface SearchFiltersState {
  query: string;
  languages: string[];
  sortBy: SortType;
  sortDirection: SortDirection;
  dateRange: {
    from: Date | null;
    to: Date | null;
  };
}

interface SearchFiltersProps {
  filters: SearchFiltersState;
  onFiltersChange: (filters: SearchFiltersState) => void;
  availableLanguages: string[];
  totalNotes: number;
  filteredCount: number;
}

export const SearchFilters: React.FC<SearchFiltersProps> = ({
  filters,
  onFiltersChange,
  availableLanguages,
  totalNotes,
  filteredCount
}) => {
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);

  // Mettre à jour un filtre spécifique
  const updateFilter = (updates: Partial<SearchFiltersState>) => {
    onFiltersChange({ ...filters, ...updates });
  };

  // Gestion des langues
  const toggleLanguage = (language: string) => {
    const languages = filters.languages.includes(language)
      ? filters.languages.filter(l => l !== language)
      : [...filters.languages, language];
    updateFilter({ languages });
  };

  // Réinitialiser tous les filtres
  const resetFilters = () => {
    onFiltersChange({
      query: "",
      languages: [],
      sortBy: "updated",
      sortDirection: "desc",
      dateRange: { from: null, to: null }
    });
  };

  // Vérifier si des filtres sont actifs
  const hasActiveFilters = filters.languages.length > 0 || 
    filters.dateRange.from !== null || 
    filters.dateRange.to !== null || 
    filters.sortBy !== "updated" || 
    filters.sortDirection !== "desc";

  // Affichage du nombre de résultats
  const renderResultsCount = () => {
    if (totalNotes === 0) return null;

    if (filteredCount === totalNotes) {
      return (
        <span className="text-xs text-gray-500 dark:text-gray-400 mr-2">
          {totalNotes} notes
        </span>
      );
    }

    return (
      <span className="text-xs text-gray-500 dark:text-gray-400 mr-2">
        {filteredCount} sur {totalNotes} notes
      </span>
    );
  };

  // Rendu des badges de filtres actifs
  const renderActiveFilters = () => {
    if (!hasActiveFilters) return null;

    return (
      <div className="flex flex-wrap gap-2 mt-2">
        {filters.languages.map(lang => (
          <Badge key={lang} variant="secondary" className="text-xs">
            {lang.toUpperCase()}
            <X 
              className="ml-1 h-3 w-3 cursor-pointer" 
              onClick={(e) => {
                e.stopPropagation();
                toggleLanguage(lang);
              }}
            />
          </Badge>
        ))}

        {filters.sortBy !== "updated" || filters.sortDirection !== "desc" ? (
          <Badge variant="secondary" className="text-xs">
            Tri: {getSortLabel()}
            <X 
              className="ml-1 h-3 w-3 cursor-pointer" 
              onClick={(e) => {
                e.stopPropagation();
                updateFilter({ sortBy: "updated", sortDirection: "desc" });
              }}
            />
          </Badge>
        ) : null}

        {(filters.dateRange.from || filters.dateRange.to) && (
          <Badge variant="secondary" className="text-xs">
            Date{filters.dateRange.from && filters.dateRange.to ? " range" : ""}
            <X 
              className="ml-1 h-3 w-3 cursor-pointer" 
              onClick={(e) => {
                e.stopPropagation();
                updateFilter({ dateRange: { from: null, to: null } });
              }}
            />
          </Badge>
        )}

        <Button 
          variant="ghost" 
          size="sm" 
          className="text-xs h-6 px-2 text-gray-500"
          onClick={resetFilters}
        >
          Réinitialiser
        </Button>
      </div>
    );
  };

  // Obtenir le label pour le tri actuel
  const getSortLabel = () => {
    const direction = filters.sortDirection === "asc" ? "croissant" : "décroissant";
    switch(filters.sortBy) {
      case "title": return `Titre (${direction})`;
      case "created": return `Date de création (${direction})`;
      case "updated": return `Dernière modification (${direction})`;
      case "language": return `Langue (${direction})`;
      default: return "";
    }
  };

  return (
    <div className="mb-3">
      <div className="flex items-center">
        <div className="relative flex-1">
          <Input
            className="pl-10 pr-10 bg-white dark:bg-gray-800 dark:text-white"
            placeholder="Rechercher dans vos notes..."
            value={filters.query}
            onChange={(e) => updateFilter({ query: e.target.value })}
          />
          <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
            <Filter className="h-4 w-4 text-gray-400" />
          </div>
          {filters.query && (
            <div className="absolute inset-y-0 right-3 flex items-center">
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-6 w-6"
                onClick={() => updateFilter({ query: "" })}
              >
                <X className="h-4 w-4 text-gray-400" />
              </Button>
            </div>
          )}
        </div>
        
        <DropdownMenu open={isFiltersOpen} onOpenChange={setIsFiltersOpen}>
          <DropdownMenuTrigger asChild>
            <Button 
              variant="outline" 
              size="icon" 
              className="ml-2 relative bg-white dark:bg-gray-800"
              aria-label="Filtres de recherche"
            >
              <Filter className="h-4 w-4" />
              {hasActiveFilters && (
                <span className="absolute -top-1 -right-1 flex h-3 w-3">
                  <span className="animate-none relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
                </span>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-72">
            <DropdownMenuGroup>
              <div className="p-2">
                <h4 className="mb-2 text-sm font-medium">Trier par</h4>
                <div className="grid grid-cols-2 gap-2">
                  <Button 
                    variant={filters.sortBy === "title" ? "default" : "outline"}
                    size="sm"
                    className="justify-start text-xs"
                    onClick={() => updateFilter({ 
                      sortBy: "title", 
                      sortDirection: filters.sortBy === "title" && filters.sortDirection === "asc" ? "desc" : "asc" 
                    })}
                  >
                    {filters.sortBy === "title" && filters.sortDirection === "asc" ? <SortAsc className="mr-1 h-3 w-3" /> : <SortDesc className="mr-1 h-3 w-3" />}
                    Titre
                  </Button>
                  
                  <Button 
                    variant={filters.sortBy === "language" ? "default" : "outline"}
                    size="sm"
                    className="justify-start text-xs"
                    onClick={() => updateFilter({ 
                      sortBy: "language", 
                      sortDirection: filters.sortBy === "language" && filters.sortDirection === "asc" ? "desc" : "asc" 
                    })}
                  >
                    {filters.sortBy === "language" && filters.sortDirection === "asc" ? <SortAsc className="mr-1 h-3 w-3" /> : <SortDesc className="mr-1 h-3 w-3" />}
                    Langue
                  </Button>
                  
                  <Button 
                    variant={filters.sortBy === "updated" ? "default" : "outline"}
                    size="sm"
                    className="justify-start text-xs"
                    onClick={() => updateFilter({ 
                      sortBy: "updated", 
                      sortDirection: filters.sortBy === "updated" && filters.sortDirection === "asc" ? "desc" : "asc" 
                    })}
                  >
                    {filters.sortBy === "updated" && filters.sortDirection === "asc" ? <SortAsc className="mr-1 h-3 w-3" /> : <SortDesc className="mr-1 h-3 w-3" />}
                    Modification
                  </Button>
                  
                  <Button 
                    variant={filters.sortBy === "created" ? "default" : "outline"}
                    size="sm"
                    className="justify-start text-xs"
                    onClick={() => updateFilter({ 
                      sortBy: "created", 
                      sortDirection: filters.sortBy === "created" && filters.sortDirection === "asc" ? "desc" : "asc" 
                    })}
                  >
                    {filters.sortBy === "created" && filters.sortDirection === "asc" ? <SortAsc className="mr-1 h-3 w-3" /> : <SortDesc className="mr-1 h-3 w-3" />}
                    Création
                  </Button>
                </div>
              </div>
              
              <DropdownMenuSeparator />
              
              <div className="p-2">
                <h4 className="mb-2 text-sm font-medium">Langues</h4>
                <div className="grid grid-cols-2 gap-1 max-h-32 overflow-y-auto">
                  {availableLanguages.map(language => (
                    <div key={language} className="flex items-center space-x-2">
                      <Checkbox 
                        id={`lang-${language}`} 
                        checked={filters.languages.includes(language)}
                        onCheckedChange={() => toggleLanguage(language)}
                      />
                      <Label 
                        htmlFor={`lang-${language}`}
                        className="text-sm font-normal cursor-pointer"
                      >
                        {language.toUpperCase()}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
              
              <DropdownMenuSeparator />
              
              <div className="p-2 flex justify-between">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={resetFilters}
                  className="text-xs"
                >
                  Réinitialiser
                </Button>
                
                <Button
                  size="sm"
                  onClick={() => setIsFiltersOpen(false)}
                  className="text-xs"
                >
                  Appliquer
                </Button>
              </div>
            </DropdownMenuGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      
      <div className="flex justify-between items-center mt-1">
        {renderResultsCount()}
        {renderActiveFilters()}
      </div>
    </div>
  );
};

// Fonction utilitaire pour filtrer et trier les notes
export const applyFilters = (notes: Note[], filters: SearchFiltersState): Note[] => {
  // Étape 1: Filtrer les notes par la requête de recherche
  let filtered = notes;
  
  if (filters.query) {
    const query = filters.query.toLowerCase();
    filtered = filtered.filter(note => 
      note.title.toLowerCase().includes(query) ||
      (note.content && note.content.toLowerCase().includes(query)) ||
      (note.translation && note.translation.toLowerCase().includes(query))
    );
  }
  
  // Étape 2: Filtrer par langue
  if (filters.languages.length > 0) {
    filtered = filtered.filter(note => 
      note.language && filters.languages.includes(note.language)
    );
  }
  
  // Étape 3: Filtrer par plage de dates
  if (filters.dateRange.from || filters.dateRange.to) {
    filtered = filtered.filter(note => {
      const noteDate = new Date(
        filters.sortBy === "created" ? note.created_at : note.updated_at
      );
      
      if (filters.dateRange.from && filters.dateRange.to) {
        return noteDate >= filters.dateRange.from && noteDate <= filters.dateRange.to;
      } else if (filters.dateRange.from) {
        return noteDate >= filters.dateRange.from;
      } else if (filters.dateRange.to) {
        return noteDate <= filters.dateRange.to;
      }
      
      return true;
    });
  }
  
  // Étape 4: Trier les résultats
  return filtered.sort((a, b) => {
    const direction = filters.sortDirection === "asc" ? 1 : -1;
    
    switch (filters.sortBy) {
      case "title":
        return direction * a.title.localeCompare(b.title);
      case "language":
        return direction * ((a.language || "").localeCompare(b.language || ""));
      case "created":
        return direction * (new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      case "updated":
      default:
        return direction * (new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime());
    }
  });
};