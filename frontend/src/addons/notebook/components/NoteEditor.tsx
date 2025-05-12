import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/use-toast";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, Save, Languages, Trash, CheckCircle } from "lucide-react";
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
import TagManager, { TagItem } from "./TagManager";
import { tagAPI } from "../api/tagAPI";

interface NoteEditorProps {
  note: Note;
  onSave: () => void;
  onCancel: () => void;
}

export function NoteEditor({ note, onSave, onCancel }: NoteEditorProps) {
  const { toast } = useToast();
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [currentTab, setCurrentTab] = useState("content");
  
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
  
  // Initialize from props when note changes
  useEffect(() => {
    if (note) {
      console.log("Loading note into editor:", {
        id: note.id,
        title: note.title,
        content: note.content?.substring(0, 20) + "...",
        translation: note.translation?.substring(0, 20) + "..."
      });

      setTitle(note.title || "");
      setContent(note.content || "");
      setTranslation(note.translation || "");
      setLanguage(note.language || "fr");
      
      // If the note has tags, initialize them
      if (note.tags) {
        setSelectedTagIds(note.tags.map(tag => tag.id));
      }
    }
  }, [note.id, note.title, note.content, note.translation, note.language, note.tags]); 
  
  // Check if tag API is available and load tags
  useEffect(() => {
    const checkTagsApi = async () => {
      try {
        const isAvailable = await tagAPI.checkTagsFeatureAvailable();
        setTagApiAvailable(isAvailable);
        
        if (isAvailable) {
          setIsLoadingTags(true);
          const fetchedTags = await tagAPI.getTags();
          setTags(fetchedTags);
        }
      } catch (error) {
        console.warn("Error checking tags API:", error);
        setTagApiAvailable(false);
      } finally {
        setIsLoadingTags(false);
      }
    };
    
    checkTagsApi();
  }, []);

  // Handle save
  const handleSave = async () => {
    if (!title.trim()) {
      toast({
        title: "Erreur",
        description: "Le titre ne peut pas être vide",
        variant: "destructive"
      });
      return;
    }
    
    setIsSaving(true);
    
    try {
      const updatedNote = {
        ...note,
        title: title.trim(),
        content: content,
        translation: translation,
        language: language
      };
      
      console.log("Saving note:", {
        id: updatedNote.id,
        title: updatedNote.title,
        contentLength: updatedNote.content?.length || 0,
        translationLength: updatedNote.translation?.length || 0
      });
      
      // Save the note
      await notebookAPI.updateNote(note.id, updatedNote);
      
      // If tag API is available, update tags
      if (tagApiAvailable) {
        // Get current tags of the note
        const currentTagIds = note.tags ? note.tags.map(tag => tag.id) : [];
        
        // Tags to add
        const tagsToAdd = selectedTagIds.filter(id => !currentTagIds.includes(id));
        
        // Tags to remove
        const tagsToRemove = currentTagIds.filter(id => !selectedTagIds.includes(id));
        
        // Add new tags
        for (const tagId of tagsToAdd) {
          await tagAPI.addTagToNote(note.id, tagId);
        }
        
        // Remove tags
        for (const tagId of tagsToRemove) {
          await tagAPI.removeTagFromNote(note.id, tagId);
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
      console.error("Error saving note:", error);
      
      toast({
        title: "Erreur",
        description: "Impossible d'enregistrer la note",
        variant: "destructive"
      });
    } finally {
      setIsSaving(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    setIsDeleting(true);
    
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
      console.error("Error deleting note:", error);
      
      toast({
        title: "Erreur",
        description: "Impossible de supprimer la note",
        variant: "destructive"
      });
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };
  
  // Handle adding a new tag
  const handleAddTag = async (name: string, color?: string): Promise<TagItem | undefined> => {
    try {
      const newTag = await tagAPI.createTag(name, color);
      setTags(prevTags => [...prevTags, newTag]);
      return newTag;
    } catch (error) {
      console.error("Error adding tag:", error);
      toast({
        title: "Erreur",
        description: "Impossible de créer le tag",
        variant: "destructive"
      });
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
  
  return (
    <motion.div
      className="h-full flex flex-col overflow-hidden"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3 }}
    >
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
              className="text-lg font-medium search-animation"
            />
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
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Loader2 className="animate-spin h-4 w-4" />
                Chargement des tags...
              </div>
            ) : (
              <TagManager
                tags={tags}
                selectedTags={selectedTagIds}
                availableTags={tags}
                onAddTag={handleAddTag}
                onRemoveTag={handleRemoveTag}
                onSelectTag={handleSelectTag}
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
                  <Textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="Contenu de la note..."
                    className="h-full w-full resize-none search-animation notebook-scrollable-area max-h-[60vh]"
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
                  <Textarea
                    value={translation}
                    onChange={(e) => setTranslation(e.target.value)}
                    placeholder="Traduction..."
                    className="h-full w-full resize-none search-animation notebook-scrollable-area max-h-[60vh]"
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
              className="text-red-500 border-red-200 hover:bg-red-50 hover:text-red-600 dark:text-red-400 dark:border-red-900 dark:hover:bg-red-900/20"
            >
              <Trash className="h-4 w-4 mr-2" />
              Supprimer
            </Button>
          </motion.div>
          
          <div className="flex gap-2">
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button variant="outline" onClick={onCancel}>
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
                disabled={isSaving}
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
            <AlertDialogCancel>Annuler</AlertDialogCancel>
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