import React, { useRef, useCallback, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Plus, FileText, Clock, Calendar } from "lucide-react";
import { Note } from "@/addons/notebook/types";
import { formatDistanceToNow, format } from "date-fns";
import { fr } from "date-fns/locale";
import { useMediaQueryHook } from "./NotebookMain";
import MarkdownPreview from "./MarkdownPreview";
import { useVirtualizer } from "@tanstack/react-virtual";

interface NoteListProps {
  notes: Note[];
  onSelectNote: (note: Note) => void;
  onCreateNote: () => void;
  selectedNoteId?: number;
  filter: string;
  onFilterChange: (filter: string) => void;
  hasMore?: boolean;
  isLoadingMore?: boolean;
  onLoadMore?: () => void;
}

// Exportation nommée pour faciliter le lazy loading
export function NoteList({
  notes,
  onSelectNote,
  onCreateNote,
  selectedNoteId,
  hasMore = false,
  isLoadingMore = false,
  onLoadMore,
}: NoteListProps) {
  // Responsive state
  const { isMobile } = useMediaQueryHook();

  // Si aucune note - version optimisée avec animations plus légères
  if (notes.length === 0) {
    return (
      <div 
        className="flex flex-col items-center justify-center h-full p-6 space-y-4 animate-fade-in"
      >
        <div 
          className="rounded-full bg-gray-100 dark:bg-gray-800 p-4"
        >
          <FileText className="h-8 w-8 text-gray-400 dark:text-gray-500" />
        </div>
        <p className="text-center text-gray-500 dark:text-gray-400">
          Vous n'avez pas encore de notes.
        </p>
        <div className="hover:scale-105 transition-transform">
          <Button 
            onClick={onCreateNote}
            className="bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400 text-white"
          >
            <Plus className="h-4 w-4 mr-2" />
            Créer une note
          </Button>
        </div>
      </div>
    );
  }

  const parentRef = useRef<HTMLDivElement>(null);

  // Créer le virtualiseur qui gère le rendu efficace d'une liste de grande taille
  const rowVirtualizer = useVirtualizer({
    count: notes.length,
    getScrollElement: () => parentRef.current,
    estimateSize: useCallback(() => 80, []), // Hauteur estimée d'une carte de note (peut être ajustée)
    overscan: 5, // Nombre d'éléments supplémentaires à rendre au-dessus et en-dessous de la vue visible
  });

  // Memoiser le rendu d'une note pour éviter les re-renders inutiles
  const renderNoteCard = useCallback((note: Note, index: number, isSelected: boolean) => {
    // Calculer le temps écoulé depuis la dernière mise à jour
    const timeAgo = formatDistanceToNow(new Date(note.updated_at), {
      addSuffix: true,
      locale: fr
    });
    
    // Format date pour affichage dans le tooltip
    const formattedDate = format(new Date(note.updated_at), 'PPP', { locale: fr });
    
    // Utiliser une div standard avec des classes de transition CSS
    // au lieu des animations framer-motion pour optimiser les performances
    return (
      <div
        key={note.id}
        className="opacity-100 note-item-appear-active selection-highlight mb-2 transition-transform duration-200 ease-out hover:translate-x-1 performance-optimized"
      >
        <Card
          onClick={() => onSelectNote(note)}
          className={`p-3 cursor-pointer transition-all ${
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
              <div className="flex items-center mt-1 space-x-2 flex-wrap">
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
                <div className="mt-1 text-sm text-gray-600 dark:text-gray-300 line-clamp-2">
                  <MarkdownPreview
                    content={note.content}
                    truncate={true}
                    maxLength={200}
                  />
                </div>
              )}
            </div>
          </div>
          
          {/* Montrer des indicateurs supplémentaires uniquement sur tablet/desktop */}
          {!isMobile && note.translation && note.translation.length > 0 && (
            <div className="mt-1 pt-1 border-t border-gray-100 dark:border-gray-800">
              <div className="text-xs text-gray-500 dark:text-gray-400 italic line-clamp-1">
                <MarkdownPreview
                  content={note.translation}
                  truncate={true}
                  maxLength={100}
                  className="text-xs italic"
                />
              </div>
            </div>
          )}
        </Card>
      </div>
    );
  }, [isMobile, onSelectNote]);

  // Ajouter un détecteur de scroll pour le chargement infini
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    if (!onLoadMore || isLoadingMore || !hasMore) return;
    
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    const scrollBottom = scrollHeight - scrollTop - clientHeight;
    
    // Quand on approche du bas, on charge plus d'éléments
    if (scrollBottom < 200) {
      onLoadMore();
    }
  };

  return (
    <div 
      ref={parentRef} 
      className="p-4 space-y-2 notebook-scrollable-area overflow-auto h-full" 
      style={{ height: '100%', overflowY: 'auto' }}
      onScroll={handleScroll}
    >
      {/* Container de hauteur égale à la totalité de la liste */}
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {/* Seulement les éléments visibles sont rendus */}
        {rowVirtualizer.getVirtualItems().map(virtualRow => {
          const note = notes[virtualRow.index];
          const isSelected = note.id === selectedNoteId;
          
          return (
            <div
              key={virtualRow.key}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                transform: `translateY(${virtualRow.start}px)`,
                paddingBottom: '8px' // Équivalent de mb-2
              }}
            >
              {renderNoteCard(note, virtualRow.index, isSelected)}
            </div>
          );
        })}
      </div>
      
      {/* Indicateur de chargement en bas de la liste */}
      {isLoadingMore && (
        <div className="py-4 text-center">
          <div className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-solid border-indigo-500 border-r-transparent"></div>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">Chargement...</p>
        </div>
      )}
      
      {/* Bouton "Charger plus" si disponible et pas en cours de chargement */}
      {hasMore && !isLoadingMore && onLoadMore && (
        <div className="py-4 text-center">
          <Button 
            onClick={onLoadMore}
            variant="outline"
            size="sm"
            className="text-xs"
          >
            Charger plus de notes
          </Button>
        </div>
      )}
    </div>
  );
}