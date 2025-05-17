import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, Save, Languages, Trash, CheckCircle, AlertCircle, RefreshCcw } from "lucide-react";
import { Note } from "@/addons/notebook/types";
import { notebookAPI } from "../api/notebookAPI";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { motion, AnimatePresence } from "framer-motion";
import TagEditor, { TagItem } from "./TagEditor";
import { tagAPI } from "../api/tagAPI";
import { useErrorHandler, ErrorType, ErrorResponse } from "../utils/errorHandling";
import ErrorDisplay from "./ErrorDisplay";
import LoadingIndicator from "./LoadingIndicator";
import MarkdownEditor from "./MarkdownEditor";
import AIAssistant from "./AIAssistant";
import ShareNoteDialog from "./ShareNoteDialog";
import "./markdown-styles.css";

interface NoteEditorProps {
  note: Note;
  onSave: () => void;
  onCancel: () => void;
  isLoading?: boolean; // Adding isLoading prop for parent-controlled loading state
}

export function NoteEditor({ note, onSave, onCancel, isLoading = false }: NoteEditorProps) {
  const { toast } = useToast();
  const { handleError } = useErrorHandler();

  // États d'UI
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [currentTab, setCurrentTab] = useState("content");

  // États d'erreur
  const [error, setError] = useState<ErrorResponse | null>(null);

  // Basic note fields
  const [title, setTitle] = useState(note?.title || "");
  const [content, setContent] = useState(note?.content || "");
  const [translation, setTranslation] = useState(note?.translation || "");
  const [language, setLanguage] = useState(note?.language || "fr");

  // Tags state
  const [tags, setTags] = useState<TagItem[]>([]);
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([]);
  const [tagApiAvailable, setTagApiAvailable] = useState(false);
  const [isLoadingTags, setIsLoadingTags] = useState(false);
  const [tagError, setTagError] = useState<ErrorResponse | null>(null);

  // État pour gérer l'affichage de l'indicateur de chargement
  const [isNoteLoading, setIsNoteLoading] = useState(false);

  // Initialize from props when note changes - version ultra simplifiée
  useEffect(() => {
    if (!note || !note.id) return;

    // Mise à jour des champs avec les données disponibles, simples et directs
    setTitle(note.title || "");
    setContent(note.content || "");
    setTranslation(note.translation || "");
    setLanguage(note.language || "fr");
    
    // Réinitialiser l'erreur
    setError(null);

    // If the note has tags, initialize them
    if (note.tags) {
      setSelectedTagIds(note.tags.map(tag => tag.id));
    } else {
      setSelectedTagIds([]);
    }
  }, [note]);

  // Check if tag API is available and load tags
  useEffect(() => {
    // Flag to track if the component is mounted
    let isMounted = true;

    const checkTagsApi = async () => {
      // Prevent multiple calls
      if (isLoadingTags) return;

      try {
        setTagError(null);
        setIsLoadingTags(true);

        // First check if the API is available (caching the result)
        const isAvailable = await tagAPI.checkTagsFeatureAvailable();

        // Check if component is still mounted before updating state
        if (!isMounted) return;

        setTagApiAvailable(isAvailable);

        if (isAvailable) {
          // Fetch tags only if API is available
          const fetchedTags = await tagAPI.getTags();

          // Check if component is still mounted
          if (!isMounted) return;

          setTags(fetchedTags);
        }
      } catch (error) {
        // Check if component is still mounted
        if (!isMounted) return;

        const parsedError = handleError(error, "Erreur de chargement des tags");
        setTagError(parsedError);
        setTagApiAvailable(false);
      } finally {
        // Check if component is still mounted
        if (isMounted) {
          setIsLoadingTags(false);
        }
      }
    };

    // Execute the check only once
    checkTagsApi();

    // Cleanup function to prevent state updates after unmount
    return () => {
      isMounted = false;
    };
  }, [handleError, isLoadingTags]);

  // Validation des données avant enregistrement
  const validateNote = (): boolean => {
    // Validation du titre
    if (!title.trim()) {
      const validationError: ErrorResponse = {
        type: ErrorType.VALIDATION,
        message: "Le titre ne peut pas être vide",
        retry: false
      };
      setError(validationError);

      toast({
        title: "Données invalides",
        description: "Le titre ne peut pas être vide",
        variant: "destructive"
      });

      return false;
    }

    // Réinitialiser les erreurs si tout est valide
    setError(null);
    return true;
  };

  // Handle save
  const handleSave = async () => {
    // Validation des données
    if (!validateNote()) return;

    setIsSaving(true);
    setError(null);

    try {
      const updatedNote = {
        ...note,
        title: title.trim(),
        content: content,
        translation: translation,
        language: language
      };

      // Save the note
      await notebookAPI.updateNote(note.id, updatedNote);

      // If tag API is available, update tags
      if (tagApiAvailable) {
        try {
          // Get current tags of the note
          const currentTagIds = note.tags ? note.tags.map(tag => tag.id) : [];

          // Tags to add
          const tagsToAdd = selectedTagIds.filter(id => !currentTagIds.includes(id));

          // Tags to remove
          const tagsToRemove = currentTagIds.filter(id => !selectedTagIds.includes(id));

          // Traitement par lots pour éviter les problèmes de concurrence
          const tagsPromises = [
            // Ajout de tags
            ...tagsToAdd.map(tagId => tagAPI.addTagToNote(note.id, tagId)),

            // Suppression de tags
            ...tagsToRemove.map(tagId => tagAPI.removeTagFromNote(note.id, tagId))
          ];

          // Attendre toutes les opérations de tags
          await Promise.all(tagsPromises);
        } catch (tagError) {
          // Si l'erreur vient des tags, on continue quand même
          // mais on affiche un avertissement
          console.warn("Erreur lors de la mise à jour des tags:", tagError);
          toast({
            title: "Avertissement",
            description: "La note a été enregistrée mais certains tags n'ont pas pu être mis à jour",
            variant: "default"
          });
        }
      }

      // Montrer l'animation de succès
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);

      toast({
        title: "Succès",
        description: "Note enregistrée avec succès"
      });

      // Notify parent
      onSave();
    } catch (error) {
      const parsedError = handleError(error, "Erreur d'enregistrement");
      setError(parsedError);
    } finally {
      setIsSaving(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    setIsDeleting(true);
    setError(null);

    try {
      await notebookAPI.deleteNote(note.id);

      toast({
        title: "Succès",
        description: "Note supprimée avec succès"
      });

      // Notify parent and close editor
      onSave();
      onCancel();
    } catch (error) {
      const parsedError = handleError(error, "Erreur de suppression");
      setError(parsedError);

      // Fermer la boîte de dialogue mais garder l'éditeur ouvert
      setShowDeleteConfirm(false);
    } finally {
      setIsDeleting(false);
    }
  };

  // Handle adding a new tag
  const handleAddTag = async (name: string, color?: string): Promise<TagItem | undefined> => {
    try {
      setTagError(null);

      // Validation
      if (!name.trim()) {
        const error = new Error("Le nom du tag ne peut pas être vide");
        handleError(error, "Validation du tag");
        return undefined;
      }

      const newTag = await tagAPI.createTag(name.trim(), color);
      setTags(prevTags => [...prevTags, newTag]);
      return newTag;
    } catch (error) {
      handleError(error, "Erreur de création de tag");
      return undefined;
    }
  };

  // Handle removing a tag
  const handleRemoveTag = (tagId: number) => {
    setSelectedTagIds(prev => prev.filter(id => id !== tagId));
  };

  // Handle selecting a tag
  const handleSelectTag = (tagId: number) => {
    setSelectedTagIds(prev =>
      prev.includes(tagId)
        ? prev.filter(id => id !== tagId)
        : [...prev, tagId]
    );
  };

  const LANGUAGE_OPTIONS = [
    { value: 'en', label: 'English' },
    { value: 'fr', label: 'French' },
    { value: 'es', label: 'Spanish' },
    { value: 'de', label: 'German' },
    { value: 'it', label: 'Italian' },
    { value: 'pt', label: 'Portuguese' }
  ];

  // Réessayer le chargement des tags
  const retryLoadTags = () => {
    setTagError(null);
    setTagApiAvailable(false);
    setIsLoadingTags(true);

    tagAPI.checkTagsFeatureAvailable()
      .then(isAvailable => {
        setTagApiAvailable(isAvailable);
        if (isAvailable) {
          return tagAPI.getTags();
        }
        return [];
      })
      .then(fetchedTags => {
        if (fetchedTags.length > 0) {
          setTags(fetchedTags);
        }
        setIsLoadingTags(false);
      })
      .catch(error => {
        const parsedError = handleError(error, "Erreur de chargement des tags");
        setTagError(parsedError);
        setTagApiAvailable(false);
        setIsLoadingTags(false);
      });
  };

  // Fonction pour recharger les détails complets de la note
  const reloadNote = () => {
    if (!note || !note.id) return;

    // Réinitialiser l'état d'erreur
    setError(null);
    
    // Indiquer que la note est en cours de chargement
    setIsNoteLoading(true);
    
    // Tenter de recharger la note
    notebookAPI.getNote(note.id)
      .then(fullNote => {
        // Mettre à jour toutes les données de la note
        setTitle(fullNote.title || "");
        setContent(fullNote.content || "");
        setTranslation(fullNote.translation || "");
        setLanguage(fullNote.language || "fr");
        
        // Si la note a des tags, les initialiser
        if (fullNote.tags) {
          setSelectedTagIds(fullNote.tags.map(tag => tag.id));
        } else {
          setSelectedTagIds([]);
        }
        
        // Toast de succès
        toast({
          title: "Succès",
          description: "La note a été rechargée avec succès",
        });
      })
      .catch(error => {
        // Configurer l'erreur pour l'afficher
        const parsedError = handleError(error, "Impossible de recharger la note");
        setError(parsedError);
      })
      .finally(() => {
        setIsNoteLoading(false);
      });
  };

  return (
    <motion.div
      className="h-full flex flex-col overflow-hidden"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3 }}
    >
      {/* Loading indicator overlay */}
      {(isNoteLoading || isLoading) && (
        <div className="absolute inset-0 bg-white/50 dark:bg-gray-900/50 flex items-center justify-center z-50">
          <LoadingIndicator message="Chargement de la note..." size="large" />
        </div>
      )}
      {/* Afficher les erreurs d'API en haut */}
      <AnimatePresence mode="wait">
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="mb-4"
          >
            <ErrorDisplay
              error={error}
              onDismiss={() => setError(null)}
              onRetry={error.type === ErrorType.LOADING ? reloadNote : handleSave}
              className="compact"
            />
          </motion.div>
        )}
      </AnimatePresence>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md px-8 py-6 flex-1 flex flex-col overflow-hidden max-h-full">
        <motion.div
          className="flex justify-between items-center mb-6"
          initial={{ y: -10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <div className="flex-1">
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Titre de la note"
              className={`text-lg font-medium search-animation ${!title.trim() ? 'border-red-300 focus:border-red-500 dark:border-red-800' : ''}`}
              aria-invalid={!title.trim()}
            />
            {!title.trim() && (
              <p className="text-xs text-red-500 mt-1 flex items-center">
                <AlertCircle className="h-3 w-3 mr-1" />
                Le titre est requis
              </p>
            )}
          </div>

          <div className="flex items-center gap-2 ml-2">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="border rounded-md p-2 bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              {LANGUAGE_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            <Badge variant="outline" className="gap-1 bg-gray-100 dark:bg-gray-800">
              <Languages className="h-3 w-3" />
              {language.toUpperCase()}
            </Badge>

            <ShareNoteDialog
              note={note}
              onUpdateSharing={onSave}
            />

            <AIAssistant
              noteContent={currentTab === "content" ? content : translation}
              noteLanguage={language}
              onApplyTranslation={(text) => setTranslation(text)}
              onAddExampleSentence={(sentence) => {
                setContent(prevContent => {
                  if (prevContent.trim()) {
                    return prevContent + '\n\n' + sentence;
                  }
                  return sentence;
                });
              }}
              onApplyCorrection={(correctedText) => {
                if (currentTab === "content") {
                  setContent(correctedText);
                } else {
                  setTranslation(correctedText);
                }
              }}
              onUpdatePronunciation={(phonetic) => {
                setContent(prevContent => {
                  if (prevContent.trim()) {
                    return prevContent + '\n\n**Pronunciation:** ' + phonetic;
                  }
                  return '**Pronunciation:** ' + phonetic;
                });
              }}
            />
          </div>
        </motion.div>

        {/* Tags section */}
        {tagApiAvailable && (
          <motion.div
            className="mb-4"
            initial={{ y: -5, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.15 }}
          >
            {isLoadingTags ? (
              <LoadingIndicator message="Chargement des tags..." size="small" inline />
            ) : tagError ? (
              <ErrorDisplay
                error={tagError}
                onDismiss={() => setTagError(null)}
                onRetry={retryLoadTags}
                className="compact"
              />
            ) : (
              <TagEditor
                allTags={tags}
                selectedTags={selectedTagIds}
                onAddTag={handleAddTag}
                onRemoveTag={handleRemoveTag}
                onSelectTag={handleSelectTag}
                onDeleteTag={async (tagId) => {
                  try {
                    await tagAPI.deleteTag(tagId);
                    // Remove this tag from the selected tags if it's selected
                    if (selectedTagIds.includes(tagId)) {
                      handleRemoveTag(tagId);
                    }
                    // Remove from the tags list
                    setTags(prevTags => prevTags.filter(tag => tag.id !== tagId));
                  } catch (error) {
                    console.error("Error deleting tag:", error);
                    toast({
                      title: "Error",
                      description: "Failed to delete tag",
                      variant: "destructive"
                    });
                  }
                }}
              />
            )}
          </motion.div>
        )}

        <Tabs
          defaultValue="content"
          className="flex-1 flex flex-col overflow-hidden"
          value={currentTab}
          onValueChange={setCurrentTab}
        >
          <TabsList className="mb-5">
            <TabsTrigger value="content">Contenu</TabsTrigger>
            <TabsTrigger value="translation">Traduction</TabsTrigger>
          </TabsList>

          <AnimatePresence mode="wait">
            {currentTab === "content" && (
                <motion.div
                  key="content-tab"
                  className="flex-1 overflow-auto"
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  transition={{ duration: 0.2 }}
                >
                  <TabsContent value="content" className="flex-1 overflow-auto h-full min-h-[300px]">
                    <MarkdownEditor
                      value={content}
                      onChange={setContent}
                      placeholder="Contenu de la note..."
                      minHeight="300px"
                      maxHeight="60vh"
                      language={language}
                    />
                  </TabsContent>
                </motion.div>
              )}

              {currentTab === "translation" && (
                <motion.div
                  key="translation-tab"
                  className="flex-1 overflow-auto"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 10 }}
                  transition={{ duration: 0.2 }}
                >
                  <TabsContent value="translation" className="flex-1 overflow-auto h-full min-h-[300px]">
                    <MarkdownEditor
                      value={translation}
                      onChange={setTranslation}
                      placeholder="Traduction..."
                      minHeight="300px"
                      maxHeight="60vh"
                      language={language}
                      isTranslation={true}
                    />
                  </TabsContent>
                </motion.div>
              )}
            </AnimatePresence>
        </Tabs>

        <motion.div
          className="flex justify-between mt-6 pt-6 border-t border-gray-100 dark:border-gray-700"
          initial={{ y: 10, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button
              variant="outline"
              onClick={() => setShowDeleteConfirm(true)}
              disabled={isDeleting}
              className="text-red-500 border-red-200 hover:bg-red-50 hover:text-red-600 dark:text-red-400 dark:border-red-900 dark:hover:bg-red-900/20"
            >
              {isDeleting ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Trash className="h-4 w-4 mr-2" />
              )}
              Supprimer
            </Button>
          </motion.div>

          <div className="flex gap-2">
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button
                variant="outline"
                onClick={onCancel}
                disabled={isSaving || isDeleting}
              >
                Annuler
              </Button>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={saveSuccess ? "save-success" : ""}
            >
              <Button
                onClick={handleSave}
                disabled={isSaving || !title.trim()}
                className="bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400 text-white"
              >
                {isSaving ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : saveSuccess ? (
                  <CheckCircle className="h-4 w-4 mr-2 text-green-200" />
                ) : (
                  <Save className="h-4 w-4 mr-2" />
                )}
                {saveSuccess ? "Sauvegardé" : "Enregistrer"}
              </Button>
            </motion.div>
          </div>
        </motion.div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <AlertDialogContent className="animate-slide-in-right">
          <AlertDialogHeader>
            <AlertDialogTitle>Êtes-vous sûr de vouloir supprimer cette note ?</AlertDialogTitle>
            <AlertDialogDescription>
              Cette action est irréversible. La note "{title}" sera définitivement supprimée.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Annuler</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-red-500 text-white hover:bg-red-600"
              disabled={isDeleting}
            >
              {isDeleting ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : null}
              Supprimer
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </motion.div>
  );
}