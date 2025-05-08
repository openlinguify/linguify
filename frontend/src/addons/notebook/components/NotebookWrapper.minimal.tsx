"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Search,
  Plus,
  BookOpenText,
  Languages,
  Bookmark,
  BookOpen,
  Star,
  Clock,
} from "lucide-react";
import { notebookAPI } from "@/addons/notebook/api/notebookAPI";
import { CategoryTree } from "./CategoryTree";
import { NoteList } from "./NoteList";
import { NoteEditor } from "./NoteEditor";
import { Category, Note } from "../types";
import { gradientText } from "@/styles/gradient_style";

export default function NotebookWrapper() {
  // State for notes, categories, and selected items
  const [notes, setNotes] = useState<Note[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | undefined>();
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  
  // Référence pour la sauvegarde automatique
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastSavedNoteRef = useRef<string>('');
  const editorRef = useRef<any>(null);
  
  // State for UI elements
  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilter, setActiveFilter] = useState("all");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  
  // États pour les filtres avancés
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [filterLanguage, setFilterLanguage] = useState<string | undefined>(undefined);
  const [filterNoteType, setFilterNoteType] = useState<string | undefined>(undefined);
  const [filterShowArchived, setFilterShowArchived] = useState<boolean>(false);
  
  // New note state
  const [newNote, setNewNote] = useState({
    title: "",
    content: "",
    note_type: "VOCABULARY",
    priority: "MEDIUM",
    language: "fr",
    example_sentences: [],
    related_words: [],
  });

  // Initial data fetch
  useEffect(() => {
    const fetchInitialData = async () => {
      setIsLoading(true);
      try {
        // Get notes - with better error handling
        let notesData: Note[] = [];
        try {
          notesData = await notebookAPI.getNotes(activeFilter);
          console.log("Successfully loaded notes:", notesData);
        } catch (error: any) {
          console.error("Failed to load notes:", error.response?.status, error.response?.data || error.message);
          notesData = []; // Use empty array as fallback
        }
        
        // Get categories - with better error handling
        let categoriesData: Category[] = [];
        try {
          categoriesData = await notebookAPI.getCategories();
          console.log("Successfully loaded categories:", categoriesData);
        } catch (error: any) {
          console.error("Failed to load categories:", error.response?.status, error.response?.data || error.message);
          categoriesData = []; // Use empty array as fallback
        }
        
        setNotes(notesData);
        setCategories(categoriesData);
      } catch (error: any) {
        console.error("Failed to fetch initial data:", error.response?.status, error.response?.data || error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchInitialData();
  }, [activeFilter]);

  // Handler for data refreshing
  const refreshData = async () => {
    try {
      const [notesData, categoriesData] = await Promise.all([
        notebookAPI.getNotes(activeFilter),
        notebookAPI.getCategories(),
      ]);
      setNotes(notesData);
      setCategories(categoriesData);
      
      // Update selected note if it's in the list
      if (selectedNote) {
        const updatedNote = notesData.find(note => note.id === selectedNote.id);
        if (updatedNote) {
          setSelectedNote(updatedNote);
        }
      }
    } catch (error) {
      console.error("Failed to refresh data:", error);
    }
  };

  // Gestionnaire de recherche avancé avec filtres
  useEffect(() => {
    const searchNotes = async () => {
      // Réinitialiser le filtre de catégorie lors d'une recherche
      if (searchTerm.trim() && selectedCategory) {
        setSelectedCategory(undefined);
      }
      
      try {
        // Afficher un indicateur de chargement
        setIsLoading(true);
        
        // Si nous avons un terme de recherche ou des filtres actifs
        if (searchTerm.trim() || filterLanguage || filterNoteType || filterShowArchived) {
          // Options de recherche avancées
          const searchOptions = {
            noteType: filterNoteType || (activeFilter !== 'all' ? activeFilter : undefined),
            language: filterLanguage,
            isArchived: filterShowArchived
          };
          
          // Effectuer la recherche avec les options
          const searchResults = await notebookAPI.searchNotes(searchTerm, searchOptions);
          
          // Tri des résultats par pertinence
          const sortedResults = [...searchResults].sort((a, b) => {
            // Les notes épinglées apparaissent en premier
            if (a.is_pinned && !b.is_pinned) return -1;
            if (!a.is_pinned && b.is_pinned) return 1;
            
            // Pertinence du titre pour le terme de recherche (si présent)
            if (searchTerm.trim()) {
              const titleExactA = a.title.toLowerCase().includes(searchTerm.toLowerCase());
              const titleExactB = b.title.toLowerCase().includes(searchTerm.toLowerCase());
              if (titleExactA && !titleExactB) return -1;
              if (!titleExactA && titleExactB) return 1;
            }
            
            // Enfin, trier par date de mise à jour
            return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
          });
          
          setNotes(sortedResults);
        } else {
          // Si aucun filtre actif, charger toutes les notes
          refreshData();
        }
      } catch (error) {
        console.error("Search failed:", error);
      } finally {
        setIsLoading(false);
      }
    };

    // Debounce pour éviter trop de requêtes pendant la frappe
    const debounce = setTimeout(searchNotes, 300);
    return () => clearTimeout(debounce);
  }, [searchTerm, activeFilter, filterLanguage, filterNoteType, filterShowArchived]);

  // Category selection handler
  const handleCategorySelect = async (categoryId: number) => {
    setSelectedCategory(categoryId);
    try {
      const categoryNotes = await notebookAPI.getNotes(`?category=${categoryId}`);
      setNotes(categoryNotes);
    } catch (error) {
      console.error("Failed to fetch category notes:", error);
    }
  };

  // Note selection handler
  const handleNoteSelect = (note: Note) => {
    setSelectedNote(note);
  };

  // Create new note handler
  const handleCreateNote = async () => {
    if (!newNote.title.trim()) return;
    
    try {
      await notebookAPI.createNote({
        ...newNote,
        category: selectedCategory
      });
      setNewNote({
        title: "",
        content: "",
        note_type: "VOCABULARY",
        priority: "MEDIUM",
        language: "fr",
        example_sentences: [],
        related_words: [],
      });
      setIsCreateDialogOpen(false);
      refreshData();
    } catch (error: any) {
      console.error("Failed to create note:", error?.response?.data || error);
      // Detailed error logging to help diagnose 400 errors
      if (error?.response?.status === 400) {
        console.error("Validation errors:", error.response.data);
      }
    }
  };

  // Initiate auto-save for current note
  const setupAutoSave = useCallback(() => {
    // Clear any existing timer
    if (autoSaveTimerRef.current) {
      clearInterval(autoSaveTimerRef.current);
    }
    
    // Set up new auto-save timer - save every 30 seconds
    autoSaveTimerRef.current = setInterval(() => {
      if (selectedNote && editorRef.current && !isSaving) {
        const currentNote = editorRef.current.getNote();
        // Convert to string for comparison
        const noteStr = JSON.stringify(currentNote);
        
        // Only save if content has changed
        if (noteStr !== lastSavedNoteRef.current) {
          console.log('Auto-saving note...');
          handleSaveNote(currentNote, true);
          lastSavedNoteRef.current = noteStr;
        }
      }
    }, 30000); // 30 seconds
    
    return () => {
      if (autoSaveTimerRef.current) {
        clearInterval(autoSaveTimerRef.current);
      }
    };
  }, [selectedNote, isSaving]);
  
  // Set up auto-save when note changes
  useEffect(() => {
    const cleanup = setupAutoSave();
    return cleanup;
  }, [selectedNote, setupAutoSave]);
  
  // Handle saving note
  const handleSaveNote = async (noteData: Partial<Note>, isAutoSave = false) => {
    if (selectedNote) {
      if (!isAutoSave) setIsSaving(true);
      try {
        await notebookAPI.updateNote(selectedNote.id, noteData);
        if (!isAutoSave) {
          refreshData();
          // Add visual feedback
          const saveIndicator = document.createElement('div');
          saveIndicator.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg z-50 animate-fade-out';
          saveIndicator.textContent = 'Note saved';
          document.body.appendChild(saveIndicator);
          
          // Remove after 2 seconds
          setTimeout(() => {
            document.body.removeChild(saveIndicator);
          }, 2000);
        }
      } catch (error) {
        console.error("Failed to update note:", error);
        if (!isAutoSave) {
          // Show error notification
          alert("Failed to save note. Please try again.");
        }
      } finally {
        if (!isAutoSave) setIsSaving(false);
      }
    }
  };

  // Handle deleting note
  const handleDeleteNote = async () => {
    if (selectedNote) {
      try {
        await notebookAPI.deleteNote(selectedNote.id);
        setSelectedNote(null);
        refreshData();
      } catch (error) {
        console.error("Failed to delete note:", error);
      }
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <div className="border-b bg-white dark:bg-gray-800 p-4 flex justify-between items-center shadow-sm">
        <div className="flex items-center">
          <BookOpen className="h-6 w-6 text-indigo-600 dark:text-indigo-400 mr-2" />
          <h1 className={`${gradientText} text-xl font-bold hidden sm:block`}>
            Language Notebook
          </h1>
        </div>
        
        <div className="flex flex-col md:flex-row gap-2 relative flex-1 max-w-md mx-4">
          <div className="relative flex-1">
            <Search
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              size={18}
            />
            <Input
              type="text"
              placeholder="Search notes..."
              className="pl-10 w-full border-gray-200 dark:border-gray-700 focus-within:ring-indigo-500 focus-within:border-indigo-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          {/* Bouton pour afficher/masquer les filtres avancés */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className="whitespace-nowrap"
          >
            {showAdvancedFilters ? "Hide Filters" : "Filters"}
          </Button>
          
          {/* Panneau de filtres avancés */}
          {showAdvancedFilters && (
            <div className="absolute top-full left-0 right-0 mt-2 p-4 bg-white dark:bg-gray-800 border rounded-lg shadow-lg z-10">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-1 block">Language</label>
                  <Select
                    value={filterLanguage || ""}
                    onValueChange={(value) => setFilterLanguage(value || undefined)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All languages" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All languages</SelectItem>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="fr">French</SelectItem>
                      <SelectItem value="es">Spanish</SelectItem>
                      <SelectItem value="de">German</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-1 block">Note Type</label>
                  <Select
                    value={filterNoteType || ""}
                    onValueChange={(value) => setFilterNoteType(value || undefined)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All types" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All types</SelectItem>
                      <SelectItem value="VOCABULARY">Vocabulary</SelectItem>
                      <SelectItem value="GRAMMAR">Grammar</SelectItem>
                      <SelectItem value="EXPRESSION">Expression</SelectItem>
                      <SelectItem value="CULTURE">Culture</SelectItem>
                      <SelectItem value="NOTE">General Note</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="mt-4 flex items-center">
                <input
                  type="checkbox"
                  id="showArchived"
                  checked={filterShowArchived}
                  onChange={(e) => setFilterShowArchived(e.target.checked)}
                  className="mr-2 h-4 w-4"
                />
                <label htmlFor="showArchived" className="text-sm">
                  Include archived notes
                </label>
              </div>
              
              <div className="mt-4 flex justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setFilterLanguage(undefined);
                    setFilterNoteType(undefined);
                    setFilterShowArchived(false);
                  }}
                  className="mr-2"
                >
                  Reset
                </Button>
                <Button
                  variant="default"
                  size="sm"
                  onClick={() => setShowAdvancedFilters(false)}
                >
                  Apply
                </Button>
              </div>
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-indigo-600 hover:bg-indigo-700 text-white flex items-center gap-2">
                <Plus size={16} />
                <span className="hidden sm:inline">New Note</span>
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle className={`${gradientText} text-xl`}>Create New Language Note</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Input
                    placeholder="Note Title"
                    value={newNote.title}
                    onChange={(e) =>
                      setNewNote({ ...newNote, title: e.target.value })
                    }
                    className="border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                  />
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <Select 
                      value={newNote.language} 
                      onValueChange={(value) => setNewNote({ ...newNote, language: value })}
                    >
                      <SelectTrigger className="border-gray-200 focus:ring-indigo-500">
                        <Languages className="h-4 w-4 mr-2 text-indigo-500" />
                        <SelectValue placeholder="Language" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="fr">French</SelectItem>
                        <SelectItem value="es">Spanish</SelectItem>
                        <SelectItem value="de">German</SelectItem>
                        <SelectItem value="it">Italian</SelectItem>
                        <SelectItem value="pt">Portuguese</SelectItem>
                        <SelectItem value="nl">Dutch</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="flex-1">
                    <Select 
                      value={newNote.note_type} 
                      onValueChange={(value) => setNewNote({ ...newNote, note_type: value })}
                    >
                      <SelectTrigger className="border-gray-200 focus:ring-indigo-500">
                        <BookOpenText className="h-4 w-4 mr-2 text-indigo-500" />
                        <SelectValue placeholder="Type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="VOCABULARY">Vocabulary</SelectItem>
                        <SelectItem value="GRAMMAR">Grammar</SelectItem>
                        <SelectItem value="EXPRESSION">Expression</SelectItem>
                        <SelectItem value="CULTURE">Culture</SelectItem>
                        <SelectItem value="NOTE">General Note</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Textarea
                    placeholder="Note Content"
                    className="min-h-[200px] border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
                    value={newNote.content}
                    onChange={(e) =>
                      setNewNote({ ...newNote, content: e.target.value })
                    }
                  />
                </div>
              </div>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setIsCreateDialogOpen(false)}
                  className="border-gray-200 hover:bg-gray-50"
                >
                  Cancel
                </Button>
                <Button 
                  onClick={handleCreateNote}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white"
                >
                  Create Note
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - Categories */}
        <div className="w-72 border-r bg-white dark:bg-gray-800 overflow-auto p-4 hidden md:flex flex-col shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h3 className={`${gradientText} font-bold text-sm flex items-center`}>
              <Bookmark className="h-4 w-4 mr-2 text-indigo-500" />
              CATEGORIES
            </h3>
            <Button 
              variant="ghost" 
              size="sm"
              className="h-7 w-7 p-0 rounded-full hover:bg-indigo-50 dark:hover:bg-indigo-900/30"
              title="Add category"
              onClick={() => {
                // Ouvrir le dialogue de création de catégorie si disponible
                const categoryTree = document.querySelector('.category-tree') as HTMLElement;
                const newCategoryButton = categoryTree?.querySelector('button[title="Add category"]') as HTMLButtonElement;
                if (newCategoryButton) {
                  newCategoryButton.click();
                }
              }}
            >
              <Plus className="h-4 w-4 text-indigo-500" />
            </Button>
          </div>
          
          <div className="overflow-auto flex-1 category-tree">
            {isLoading && categories.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-500"></div>
                <p className="text-sm text-gray-500 mt-2">Chargement des catégories...</p>
              </div>
            ) : (
              <CategoryTree 
                categories={categories} 
                selectedCategory={selectedCategory} 
                onSelect={handleCategorySelect}
              />
            )}
          </div>
          
          <div className="mt-4">
            <div className="bg-gray-50 dark:bg-gray-900/30 p-3 rounded-lg">
              <div className="text-xs text-gray-500 mb-2">RACCOURCIS</div>
              <div className="space-y-1">
                <div 
                  className="flex items-center p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                  onClick={() => {
                    setActiveFilter('favorites');
                    setSelectedCategory(undefined);
                  }}
                >
                  <Star className="h-4 w-4 text-yellow-500 mr-2" />
                  <span className="text-sm">Notes épinglées</span>
                </div>
                <div 
                  className="flex items-center p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                  onClick={() => {
                    setActiveFilter('recent');
                    setSelectedCategory(undefined);
                  }}
                >
                  <Clock className="h-4 w-4 text-blue-500 mr-2" />
                  <span className="text-sm">Notes récentes</span>
                </div>
                <div 
                  className="flex items-center p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                  onClick={() => {
                    setActiveFilter('review');
                    setSelectedCategory(undefined);
                  }}
                >
                  <BookOpen className="h-4 w-4 text-green-500 mr-2" />
                  <span className="text-sm">À réviser</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Center - Note List or Editor */}
        <div className="flex flex-1 overflow-hidden">
          {!selectedNote ? (
            <div className="w-full md:w-1/3 xl:w-1/4 border-r overflow-auto bg-white dark:bg-gray-800 shadow-sm">
              <div className="p-4">
                <Tabs
                  defaultValue="all"
                  className="w-full"
                  onValueChange={setActiveFilter}
                >
                  <TabsList className="w-full grid grid-cols-4 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
                    <TabsTrigger 
                      value="all" 
                      className="data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600 data-[state=active]:text-indigo-600 dark:data-[state=active]:text-indigo-400 data-[state=active]:shadow-sm rounded-md"
                    >
                      All
                    </TabsTrigger>
                    <TabsTrigger 
                      value="recent" 
                      className="data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600 data-[state=active]:text-indigo-600 dark:data-[state=active]:text-indigo-400 data-[state=active]:shadow-sm rounded-md"
                    >
                      Recent
                    </TabsTrigger>
                    <TabsTrigger 
                      value="review" 
                      className="data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600 data-[state=active]:text-indigo-600 dark:data-[state=active]:text-indigo-400 data-[state=active]:shadow-sm rounded-md"
                    >
                      Review
                    </TabsTrigger>
                    <TabsTrigger 
                      value="favorites" 
                      className="data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600 data-[state=active]:text-indigo-600 dark:data-[state=active]:text-indigo-400 data-[state=active]:shadow-sm rounded-md"
                    >
                      Pinned
                    </TabsTrigger>
                  </TabsList>
                  
                  <div className="mt-4">
                    <NoteList 
                      notes={notes} 
                      onNoteSelect={handleNoteSelect} 
                      onCreateNote={() => setIsCreateDialogOpen(true)}
                    />
                  </div>
                </Tabs>
              </div>
            </div>
          ) : (
            <div className="flex-1 overflow-auto bg-white dark:bg-gray-800 shadow-sm">
              <div className="max-w-4xl mx-auto p-6">
                <NoteEditor 
                  note={selectedNote} 
                  categories={categories} 
                  onSave={handleSaveNote}
                  onDelete={handleDeleteNote}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}