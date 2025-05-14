import React, { useState, useEffect } from "react";
import { NoteList } from "./NoteList";
import { NoteEditor } from "./NoteEditor";
import { useToast } from "@/components/ui/use-toast";
import { Note } from "../types";
import { notebookAPI } from "../api/notebookAPI";
import { Plus, RefreshCcw, Menu, ChevronLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useMediaQuery } from "@/hooks/use-media-query";
import { SearchFilters, SearchFiltersState, applyFilters } from "./SearchFilters";
import { ErrorType, ErrorResponse } from "../utils/errorHandling";
import ErrorDisplay from "./ErrorDisplay";
import LoadingIndicator from "./LoadingIndicator";
import ReviewReminder from "./ReviewReminder";

interface CreateNoteFormProps {
  onSubmit: (title: string, language: string) => void;
  onCancel: () => void;
}

function CreateNoteForm({ onSubmit, onCancel }: CreateNoteFormProps) {
  const [title, setTitle] = useState("");
  const [language, setLanguage] = useState("fr");
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      onSubmit(title.trim(), language);
    }
  };
  
  const LANGUAGE_OPTIONS = [
    { value: 'en', label: 'English' },
    { value: 'fr', label: 'French' },
    { value: 'es', label: 'Spanish' },
    { value: 'de', label: 'German' },
    { value: 'it', label: 'Italian' },
    { value: 'pt', label: 'Portuguese' }
  ];
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold mb-4 dark:text-white">Créer une nouvelle note</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1 dark:text-gray-200">Titre</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Titre de la note"
            className="border rounded-md p-2 w-full dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1 dark:text-gray-200">Langue</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="border rounded-md p-2 w-full dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          >
            {LANGUAGE_OPTIONS.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        
        <div className="flex justify-end gap-2 pt-2">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            className="px-4 py-2"
          >
            Annuler
          </Button>
          
          <Button
            type="submit"
            className="px-4 py-2 bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400 text-white"
          >
            Créer
          </Button>
        </div>
      </form>
    </div>
  );
}

// Hook personnalisé pour gérer la largeur d'écran
export const useMediaQueryHook = () => {
  // Définir les breakpoints
  const isMobile = useMediaQuery("(max-width: 767px)");
  const isTablet = useMediaQuery("(min-width: 768px) and (max-width: 1023px)");
  const isDesktop = useMediaQuery("(min-width: 1024px)");
  
  return { isMobile, isTablet, isDesktop };
};

export default function NotebookMain() {
  const { toast } = useToast();
  
  // État pour le responsive
  const { isMobile, isTablet, isDesktop } = useMediaQueryHook();
  const [sidebarVisible, setSidebarVisible] = useState(true);
  
  // State
  const [notes, setNotes] = useState<Note[]>([]);
  const [filteredNotes, setFilteredNotes] = useState<Note[]>([]);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  
  // État pour les filtres de recherche
  const [searchFilters, setSearchFilters] = useState<SearchFiltersState>({
    query: "",
    languages: [],
    sortBy: "updated",
    sortDirection: "desc",
    dateRange: { from: null, to: null }
  });
  
  // Liste des langues disponibles (extraites des notes)
  const [availableLanguages, setAvailableLanguages] = useState<string[]>([]);
  
  // Gérer la visibilité du sidebar en fonction de la taille d'écran
  useEffect(() => {
    if (isMobile) {
      // Sur mobile, masquer la sidebar par défaut si une note est sélectionnée
      setSidebarVisible(!selectedNote);
    } else {
      // Sur desktop ou tablette, toujours afficher la sidebar
      setSidebarVisible(true);
    }
  }, [isMobile, isTablet, isDesktop, selectedNote]);
  
  // Load notes on mount
  useEffect(() => {
    loadNotes();
  }, []);
  
  // Appliquer les filtres aux notes
  useEffect(() => {
    if (notes.length === 0) return;
    
    const filtered = applyFilters(notes, searchFilters);
    setFilteredNotes(filtered);
    
    // Extraire les langues uniques disponibles
    const languages = [...new Set(notes.filter(n => n.language).map(n => n.language))];
    setAvailableLanguages(languages as string[]);
  }, [notes, searchFilters]);
  
  // Load notes from API
  const loadNotes = async () => {
    try {
      setIsLoading(true);
      setLoadError(null);

      // Appliquer les bonnes pratiques pour la gestion des erreurs
      const notesData = await notebookAPI.getNotes();

      // Vérifier que les données sont valides
      if (!Array.isArray(notesData)) {
        throw new Error("Format de données invalide");
      }

      setNotes(notesData);

      // Apply filters to the new data
      const filtered = applyFilters(notesData, searchFilters);
      setFilteredNotes(filtered);

      // Extract unique languages (en filtrant les valeurs vides ou nulles)
      const languages = [...new Set(
        notesData
          .filter(n => n.language && n.language.trim() !== "")
          .map(n => n.language)
      )];
      setAvailableLanguages(languages as string[]);

      // If we have a selected note, reload it
      if (selectedNote) {
        const updatedNote = notesData.find(n => n.id === selectedNote.id);
        if (updatedNote) {
          setSelectedNote(updatedNote);
        } else {
          // Si la note sélectionnée n'est plus présente (supprimée par une autre session)
          setSelectedNote(null);
        }
      }
    } catch (error) {
      // Journaliser l'erreur pour le débogage
      console.error("Failed to load notes:", error);

      // Définir un message d'erreur contextuel
      let errorMessage = "Impossible de charger les notes. Veuillez réessayer.";

      if (error instanceof Error) {
        // Personnaliser le message en fonction du type d'erreur
        if (error.message.includes("network") || error.message.includes("connexion")) {
          errorMessage = "Impossible de charger les notes: problème de connexion au serveur.";
        } else if (error.message.includes("authentification") || error.message.includes("unauthorized")) {
          errorMessage = "Authentification requise pour accéder à vos notes.";
        } else if (error.message.includes("format") || error.message.includes("invalide")) {
          errorMessage = "Format de données invalide reçu du serveur.";
        }
      }

      setLoadError(errorMessage);

      // Afficher une notification pour informer l'utilisateur
      toast({
        title: "Erreur de chargement",
        description: errorMessage,
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle selecting a note
  const handleSelectNote = async (note: Note) => {
    try {
      // Vérifier que la note est valide
      if (!note || !note.id) {
        toast({
          title: "Erreur",
          description: "Cette note est invalide ou a été supprimée",
          variant: "destructive"
        });
        return;
      }

      // First set the note to show something immediately (pour une meilleure UX)
      setSelectedNote(note);

      // Sur mobile, masquer la sidebar après avoir sélectionné une note
      if (isMobile) {
        setSidebarVisible(false);
      }

      // Indiquer visuellement que la note complète est en cours de chargement
      // (L'idéal serait d'ajouter un indicateur de chargement dans le composant NoteEditor)

      // Then load the full note details with error handling
      try {
        const fullNote = await notebookAPI.getNote(note.id);

        // Vérifier que la note n'a pas disparu entre temps
        if (!fullNote) {
          throw new Error("La note n'existe plus");
        }

        // Mettre à jour la note avec tous ses détails
        setSelectedNote(fullNote);
      } catch (error) {
        // En cas d'erreur de chargement des détails, on garde la note partielle
        // mais on informe l'utilisateur
        console.error("Error loading note details:", error);

        // Déterminer un message approprié
        let errorMessage = "Impossible de charger les détails de la note";

        if (error instanceof Error) {
          if (error.message.includes("existe plus") || error.message.includes("not found")) {
            errorMessage = "Cette note n'existe plus ou a été supprimée";
          } else if (error.message.includes("réseau") || error.message.includes("network")) {
            errorMessage = "Problème de connexion lors du chargement des détails";
          }
        }

        toast({
          title: "Attention",
          description: errorMessage,
          variant: "destructive"
        });
      }
    } catch (error) {
      // Erreur générale (ne devrait pas arriver mais on gère quand même)
      console.error("Unexpected error in handleSelectNote:", error);

      setSelectedNote(null);

      toast({
        title: "Erreur",
        description: "Une erreur inattendue s'est produite",
        variant: "destructive"
      });
    }
  };
  
  // Handle creating a new note
  const handleCreateNote = async (title: string, language: string) => {
    // Validation préliminaire des données
    if (!title || title.trim() === '') {
      toast({
        title: "Validation",
        description: "Le titre ne peut pas être vide",
        variant: "destructive"
      });
      return;
    }

    try {
      // Préparer les données de la nouvelle note
      const noteData = {
        title: title.trim(),
        language: language || 'fr', // Valeur par défaut si language est vide
        content: "",
        translation: "",
        example_sentences: [],
        related_words: []
      };

      // Créer la note
      const newNote = await notebookAPI.createNote(noteData);

      // Vérifier que la note a bien été créée
      if (!newNote || !newNote.id) {
        throw new Error("La note n'a pas pu être créée correctement");
      }

      // Notification de succès
      toast({
        title: "Succès",
        description: "Note créée avec succès"
      });

      // Recharger toutes les notes pour être sûr d'avoir la liste à jour
      await loadNotes();

      // Sélectionner la nouvelle note
      setSelectedNote(newNote);

      // Fermer le formulaire de création
      setIsCreating(false);

      // Sur mobile, masquer la sidebar après avoir créé une note
      if (isMobile) {
        setSidebarVisible(false);
      }
    } catch (error) {
      // Journaliser l'erreur
      console.error("Error creating note:", error);

      // Déterminer un message approprié
      let errorMessage = "Impossible de créer la note";

      if (error instanceof Error) {
        if (error.message.includes("validation") || error.message.includes("titre")) {
          errorMessage = "Le titre de la note est invalide";
        } else if (error.message.includes("réseau") || error.message.includes("network")) {
          errorMessage = "Problème de connexion lors de la création de la note";
        } else if (error.message.includes("authentification") || error.message.includes("unauthorized")) {
          errorMessage = "Vous devez être connecté pour créer une note";
        }
      }

      // Afficher la notification d'erreur
      toast({
        title: "Erreur",
        description: errorMessage,
        variant: "destructive"
      });
    }
  };
  
  // Revenir à la liste des notes (pour mobile)
  const handleBackToList = () => {
    if (isMobile) {
      setSidebarVisible(true);
    }
  };
  
  // Annuler l'édition d'une note
  const handleCancelEdit = () => {
    setSelectedNote(null);
    
    // Sur mobile, revenir à la liste
    if (isMobile) {
      setSidebarVisible(true);
    }
  };
  
  // Render create form
  if (isCreating) {
    return (
      <div className="h-full flex flex-col">
        
        <div className="flex-1 overflow-auto p-4">
          <div className="max-w-2xl mx-auto">
            <CreateNoteForm
              onSubmit={handleCreateNote}
              onCancel={() => setIsCreating(false)}
            />
          </div>
        </div>
      </div>
    );
  }
  
  // Render loading state
  if (isLoading && notes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingIndicator
          message="Chargement des notes..."
          size="large"
          fullHeight
        />
      </div>
    );
  }
  
  // Render error state
  if (loadError) {
    const errorObject: ErrorResponse = {
      type: ErrorType.UNKNOWN, // Par défaut
      message: loadError,
      retry: true
    };

    // Déterminer le type d'erreur en fonction du message
    if (loadError.includes("connexion") || loadError.includes("réseau")) {
      errorObject.type = ErrorType.NETWORK;
    } else if (loadError.includes("authentification") || loadError.includes("connecté")) {
      errorObject.type = ErrorType.AUTHENTICATION;
    } else if (loadError.includes("format") || loadError.includes("invalide")) {
      errorObject.type = ErrorType.VALIDATION;
      errorObject.retry = false;
    } else if (loadError.includes("serveur")) {
      errorObject.type = ErrorType.SERVER;
    }

    return (
      <div className="h-full flex flex-col">
        <div className="p-4 bg-white dark:bg-gray-800 shadow-lg z-10 sticky top-0 left-0 right-0">
          <div className="flex items-center justify-between">

            <Button
              variant="outline"
              onClick={loadNotes}
              className="bg-white dark:bg-gray-800"
            >
              <RefreshCcw className="h-4 w-4 mr-2" />
              Réessayer
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-auto p-4">
          <ErrorDisplay
            error={errorObject}
            onRetry={loadNotes}
          />
        </div>
      </div>
    );
  }
  
  // Render normal view
  return (
    <div className="h-full flex flex-col overflow-hidden notebook-scroll-container">
      {/* Header - fixed pour éviter le chevauchement */}
      <div className="px-6 py-4 bg-white dark:bg-gray-800 shadow-lg z-10 sticky top-0 left-0 right-0 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            {/* Bouton retour pour mobile quand on affiche une note */}
            {isMobile && selectedNote && !sidebarVisible && (
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={handleBackToList}
                className="mr-2"
              >
                <ChevronLeft className="h-5 w-5" />
              </Button>
            )}
            
            {/* Afficher le titre d'une note spécifique sur mobile */}
            {isMobile && selectedNote && !sidebarVisible ? (
              <h2 className="text-lg font-medium truncate max-w-[200px] dark:text-white">
                {selectedNote.title}
              </h2>
            ) : (
              <h1 className="text-2xl font-bold bg-gradient-to-r from-brand-purple to-brand-gold text-transparent bg-clip-text">
                Carnet de Notes
              </h1>
            )}
          </div>
          
          <div className="flex gap-2">
            {/* Bouton menu/toggle pour mobile */}
            {isMobile && selectedNote && (
              <Button
                variant="outline"
                size="icon"
                onClick={() => setSidebarVisible(!sidebarVisible)}
                className="bg-white dark:bg-gray-800"
              >
                <Menu className="h-4 w-4" />
              </Button>
            )}
            
            {/* Bouton refresh */}
            <ReviewReminder
              onReviewNote={(noteId) => {
                // Find the note in our list and select it
                const noteToSelect = notes.find(n => n.id === noteId);
                if (noteToSelect) {
                  handleSelectNote(noteToSelect);
                }
                // Refresh notes to update review status
                loadNotes();
              }}
            />

            <Button
              variant="outline"
              onClick={loadNotes}
              disabled={isLoading}
              className="bg-white dark:bg-gray-800"
            >
              <RefreshCcw className="h-4 w-4" />
            </Button>

            {/* Bouton nouvelle note */}
            <Button
              onClick={() => setIsCreating(true)}
              className="bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400 text-white"
            >
              <Plus className="h-4 w-4 mr-2" />
              {isMobile ? "" : "Nouvelle note"}
            </Button>
          </div>
        </div>
        
        {/* Afficher les filtres de recherche uniquement si la sidebar est visible ou sur desktop */}
        {(sidebarVisible || !isMobile) && (
          <div className="mt-4">
            <SearchFilters 
              filters={searchFilters}
              onFiltersChange={setSearchFilters}
              availableLanguages={availableLanguages}
              totalNotes={notes.length}
              filteredCount={filteredNotes.length}
            />
          </div>
        )}
      </div>
      
      {/* Corps principal avec défilement indépendant */}
      <div className="flex-1 overflow-hidden notebook-content-area">
        <div className="flex h-full overflow-hidden">
          {/* Sidebar - masquée sur mobile en mode édition */}
          {(sidebarVisible || !isMobile) && (
            <div className={`${isMobile ? 'w-full' : isTablet ? 'w-80' : 'w-96'} border-r border-gray-200 dark:border-gray-700 overflow-hidden transition-all duration-300 ease-in-out`}>
              <NoteList
                notes={filteredNotes}
                onSelectNote={handleSelectNote}
                onCreateNote={() => setIsCreating(true)}
                selectedNoteId={selectedNote?.id}
                filter={searchFilters.query}
                onFilterChange={(filter) => setSearchFilters(prev => ({ ...prev, query: filter }))}
              />
            </div>
          )}
          
          {/* Zone d'édition - plein écran sur mobile, sinon flexible */}
          {(!isMobile || !sidebarVisible) && (
            <div className={`${isMobile ? 'w-full' : 'flex-1'} overflow-hidden transition-all duration-300 ease-in-out`}>
              {selectedNote ? (
                <NoteEditor
                  note={selectedNote}
                  onSave={loadNotes}
                  onCancel={handleCancelEdit}
                />
              ) : (
                <div className="h-full flex items-center justify-center p-4">
                  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 text-center max-w-md">
                    <p className="text-lg text-gray-500 dark:text-gray-400 mb-4">
                      Sélectionnez une note pour la modifier ou créez-en une nouvelle
                    </p>
                    <Button
                      onClick={() => setIsCreating(true)}
                      className="bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400 text-white"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Créer une nouvelle note
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}