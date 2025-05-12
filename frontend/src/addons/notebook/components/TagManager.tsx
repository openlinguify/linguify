import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { X, Plus, Tag, Check, Trash } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Command,
  CommandInput,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandList,
} from "@/components/ui/command";

// Interface pour les tags
export interface TagItem {
  id: number;
  name: string;
  color: string;
}

interface TagManagerProps {
  tags: TagItem[];
  selectedTags: number[];
  availableTags: TagItem[];
  onAddTag: (tag: string, color?: string) => Promise<TagItem | undefined>;
  onRemoveTag: (tagId: number) => void;
  onSelectTag: (tagId: number) => void;
}

const TAG_COLORS = [
  { name: "gray", value: "#6B7280" },
  { name: "red", value: "#EF4444" },
  { name: "orange", value: "#F97316" },
  { name: "amber", value: "#F59E0B" },
  { name: "yellow", value: "#EAB308" },
  { name: "lime", value: "#84CC16" },
  { name: "green", value: "#22C55E" },
  { name: "emerald", value: "#10B981" },
  { name: "teal", value: "#14B8A6" },
  { name: "cyan", value: "#06B6D4" },
  { name: "sky", value: "#0EA5E9" },
  { name: "blue", value: "#3B82F6" },
  { name: "indigo", value: "#6366F1" },
  { name: "violet", value: "#8B5CF6" },
  { name: "purple", value: "#A855F7" },
  { name: "fuchsia", value: "#D946EF" },
  { name: "pink", value: "#EC4899" },
  { name: "rose", value: "#F43F5E" },
];

export const TagManager: React.FC<TagManagerProps> = ({
  tags,
  selectedTags,
  availableTags,
  onAddTag,
  onRemoveTag,
  onSelectTag,
}) => {
  const [isCreating, setIsCreating] = useState(false);
  const [newTagName, setNewTagName] = useState("");
  const [selectedColor, setSelectedColor] = useState(TAG_COLORS[0].value);
  const [isOpen, setIsOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus l'input quand le mode création est activé
  useEffect(() => {
    if (isCreating && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isCreating]);

  // Gérer la soumission d'un nouveau tag
  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }
    
    if (!newTagName.trim()) return;
    
    try {
      setIsSubmitting(true);
      const newTag = await onAddTag(newTagName.trim(), selectedColor);
      
      if (newTag) {
        // Sélectionner automatiquement le nouveau tag
        onSelectTag(newTag.id);
        
        // Réinitialiser le formulaire
        setNewTagName("");
        setSelectedColor(TAG_COLORS[Math.floor(Math.random() * TAG_COLORS.length)].value);
        setIsCreating(false);
      }
    } catch (error) {
      console.error("Error adding tag:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Générer un style pour le badge de tag
  const getTagStyle = (color: string) => {
    const isLight = color === "#FFFFFF" || color === "#F9FAFB";
    
    return {
      backgroundColor: color + "20", // Légère transparence
      color: isLight ? "#374151" : color,
      borderColor: color + "40"
    };
  };

  // Rendre le bouton d'ajout de tag
  const renderAddButton = () => (
    <Button
      variant="outline"
      size="sm"
      className="flex items-center h-8"
      onClick={() => setIsCreating(true)}
    >
      <Plus className="h-4 w-4 mr-1" />
      <span>Tag</span>
    </Button>
  );

  // Rendre le formulaire de création de tag
  const renderCreateForm = () => (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <div className="flex items-center border rounded-md overflow-hidden">
        <div 
          className="h-8 w-8 flex items-center justify-center cursor-pointer"
          style={{ backgroundColor: selectedColor + "40" }}
          onClick={() => setIsOpen(true)}
        >
          <div 
            className="rounded-full h-4 w-4" 
            style={{ backgroundColor: selectedColor }} 
          />
        </div>
        
        <Input
          ref={inputRef}
          value={newTagName}
          onChange={(e) => setNewTagName(e.target.value)}
          placeholder="Nouveau tag..."
          className="border-0 h-8 px-2"
          disabled={isSubmitting}
        />
        
        {newTagName && (
          <div className="flex gap-1 pr-2">
            <button
              type="button"
              className="h-6 w-6 inline-flex items-center justify-center rounded-full text-gray-400 hover:text-gray-500 hover:bg-gray-100"
              onClick={() => setNewTagName("")}
            >
              <X className="h-3 w-3" />
            </button>
            
            <button
              type="submit"
              className="h-6 w-6 inline-flex items-center justify-center rounded-full text-green-600 hover:text-green-700 hover:bg-green-50"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <span className="animate-pulse">...</span>
              ) : (
                <Check className="h-3 w-3" />
              )}
            </button>
          </div>
        )}
      </div>
      
      {/* Sélecteur de couleur */}
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <span></span>
        </PopoverTrigger>
        <PopoverContent className="p-2 w-60" side="right">
          <div className="grid grid-cols-6 gap-1">
            {TAG_COLORS.map((color) => (
              <div
                key={color.value}
                className="h-6 w-6 rounded-full cursor-pointer relative hover:opacity-80 transition-opacity"
                style={{ backgroundColor: color.value }}
                onClick={() => {
                  setSelectedColor(color.value);
                  setIsOpen(false);
                }}
              >
                {selectedColor === color.value && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="h-2 w-2 rounded-full bg-white" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </PopoverContent>
      </Popover>
      
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8"
        onClick={() => setIsCreating(false)}
      >
        <X className="h-4 w-4" />
      </Button>
    </form>
  );

  // Rendre le sélecteur de tags
  const renderTagSelector = () => (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="flex items-center h-8"
        >
          <Tag className="h-4 w-4 mr-1" />
          <span>Sélectionner</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="p-0 w-60">
        <Command>
          <CommandInput placeholder="Rechercher un tag..." />
          <CommandList>
            <CommandEmpty>Aucun tag trouvé</CommandEmpty>
            <CommandGroup heading="Tags disponibles">
              {availableTags.length === 0 ? (
                <div className="py-2 px-3 text-sm text-gray-500">
                  Aucun tag disponible
                </div>
              ) : (
                availableTags.map((tag) => {
                  const isSelected = selectedTags.includes(tag.id);
                  return (
                    <CommandItem
                      key={tag.id}
                      onSelect={() => onSelectTag(tag.id)}
                      className="flex items-center gap-2"
                    >
                      <div
                        className="h-3 w-3 rounded-full"
                        style={{ backgroundColor: tag.color }}
                      />
                      <span>{tag.name}</span>
                      {isSelected && (
                        <Check className="h-4 w-4 ml-auto text-green-500" />
                      )}
                    </CommandItem>
                  );
                })
              )}
            </CommandGroup>
          </CommandList>
          <div className="border-t p-2">
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start"
              onClick={() => {
                setIsCreating(true);
                setIsOpen(false);
              }}
            >
              <Plus className="h-4 w-4 mr-1" />
              <span>Créer un nouveau tag</span>
            </Button>
          </div>
        </Command>
      </PopoverContent>
    </Popover>
  );

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        {isCreating ? renderCreateForm() : (
          <>
            {renderAddButton()}
            {renderTagSelector()}
          </>
        )}
      </div>
      
      {/* Liste des tags sélectionnés */}
      {selectedTags.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          <AnimatePresence>
            {selectedTags.map((tagId) => {
              const tag = tags.find((t) => t.id === tagId);
              if (!tag) return null;
              
              return (
                <motion.div
                  key={tag.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{ duration: 0.2 }}
                >
                  <Badge
                    variant="outline"
                    className="flex items-center gap-1 py-1"
                    style={getTagStyle(tag.color)}
                  >
                    <div
                      className="h-2 w-2 rounded-full"
                      style={{ backgroundColor: tag.color }}
                    />
                    <span>{tag.name}</span>
                    <button
                      className="ml-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 p-0.5"
                      onClick={() => onRemoveTag(tag.id)}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
};

export default TagManager;