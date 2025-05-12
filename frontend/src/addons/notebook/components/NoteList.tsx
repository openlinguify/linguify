import React from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plus, FileText, Clock, Calendar } from "lucide-react";
import { Note } from "@/addons/notebook/types";
import { formatDistanceToNow, format } from "date-fns";
import { fr } from "date-fns/locale";
import { useMediaQueryHook } from "./NotebookMain";
import { motion, AnimatePresence } from "framer-motion";

interface NoteListProps {
  notes: Note[];
  onSelectNote: (note: Note) => void;
  onCreateNote: () => void;
  selectedNoteId?: number;
  filter: string;
  onFilterChange: (filter: string) => void;
}

export function NoteList({
  notes,
  onSelectNote,
  onCreateNote,
  selectedNoteId,
}: NoteListProps) {
  // Responsive state
  const { isMobile } = useMediaQueryHook();

  // Si aucune note
  if (notes.length === 0) {
    return (
      <motion.div 
        className="flex flex-col items-center justify-center h-full p-6 space-y-4"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div 
          className="rounded-full bg-gray-100 dark:bg-gray-800 p-4"
          animate={{ 
            scale: [1, 1.05, 1],
            rotate: [0, 2, 0, -2, 0] 
          }}
          transition={{ 
            duration: 2, 
            ease: "easeInOut", 
            repeat: Infinity,
            repeatDelay: 1
          }}
        >
          <FileText className="h-8 w-8 text-gray-400 dark:text-gray-500" />
        </motion.div>
        <p className="text-center text-gray-500 dark:text-gray-400">
          Vous n'avez pas encore de notes.
        </p>
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Button 
            onClick={onCreateNote}
            className="bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400 text-white floating-button"
          >
            <Plus className="h-4 w-4 mr-2" />
            Créer une note
          </Button>
        </motion.div>
      </motion.div>
    );
  }

  return (
    <div className="p-6 space-y-4 notebook-scrollable-area">
      <AnimatePresence>
        {notes.map((note, index) => {
          const isSelected = note.id === selectedNoteId;
          
          // Calculer le temps écoulé depuis la dernière mise à jour
          const timeAgo = formatDistanceToNow(new Date(note.updated_at), {
            addSuffix: true,
            locale: fr
          });
          
          // Format date pour affichage dans le tooltip
          const formattedDate = format(new Date(note.updated_at), 'PPP', { locale: fr });
          
          return (
            <motion.div
              key={note.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ 
                duration: 0.2, 
                delay: index * 0.03,
                ease: "easeOut"
              }}
              className="selection-highlight mb-3"
              whileHover={{ x: 2, boxShadow: "0 4px 12px rgba(0,0,0,0.05)" }}
            >
              <Card
                onClick={() => onSelectNote(note)}
                className={`p-4 cursor-pointer transition-all ${
                  isSelected 
                    ? "border-2 border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20" 
                    : "border border-gray-200 dark:border-gray-700 hover:border-indigo-200 dark:hover:border-indigo-700"
                }`}
              >
                <div className="flex items-start space-x-2">
                  <div className="flex-shrink-0 mt-1">
                    <FileText className={`h-4 w-4 ${isSelected ? "text-indigo-500" : "text-gray-400 dark:text-gray-500"}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className={`font-medium truncate ${isSelected ? "text-indigo-700 dark:text-indigo-300" : "dark:text-white"}`}>
                      {note.title}
                    </h3>
                    <div className="flex items-center mt-2 space-x-2 flex-wrap">
                      {note.language && (
                        <Badge variant="outline" className="text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200">
                          {note.language.toUpperCase()}
                        </Badge>
                      )}
                      <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 truncate" title={formattedDate}>
                        <Clock className="h-3 w-3 mr-1 inline-flex" />
                        {timeAgo}
                      </div>
                    </div>
                    {note.content && (
                      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
                        {note.content}
                      </p>
                    )}
                  </div>
                </div>
                
                {/* Montrer des indicateurs supplémentaires uniquement sur tablet/desktop */}
                {!isMobile && note.translation && note.translation.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-100 dark:border-gray-800">
                    <p className="text-xs text-gray-500 dark:text-gray-400 italic line-clamp-1">
                      {note.translation}
                    </p>
                  </div>
                )}
              </Card>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}