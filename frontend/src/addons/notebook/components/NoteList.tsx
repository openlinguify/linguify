// src/components/notes/NoteList.tsx
import React from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Plus, 
  Bookmark, Clock, Languages, 
  BookOpenText, Volume2
} from 'lucide-react';
import { NoteListProps } from '@/addons/notebook/types/';

// Map for note types to icons and colors
const NOTE_TYPE_CONFIG = {
  VOCABULARY: { 
    icon: Languages, 
    color: 'text-emerald-500',
    bgColor: 'bg-emerald-50 dark:bg-emerald-900/20' 
  },
  GRAMMAR: { 
    icon: BookOpenText, 
    color: 'text-blue-500',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20'
  },
  EXPRESSION: { 
    icon: Volume2, 
    color: 'text-purple-500',
    bgColor: 'bg-purple-50 dark:bg-purple-900/20'
  },
  CULTURE: { 
    icon: Bookmark, 
    color: 'text-amber-500',
    bgColor: 'bg-amber-50 dark:bg-amber-900/20'
  },
  NOTE: { 
    icon: BookOpenText, 
    color: 'text-gray-500',
    bgColor: 'bg-gray-50 dark:bg-gray-700/50' 
  },
};

export function NoteList({ notes, onNoteSelect, onCreateNote }: NoteListProps) {
  // Format date in relative time
  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffInSeconds < 60) {
      return 'just now';
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes}m ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours}h ago`;
    } else if (diffInSeconds < 604800) { // 7 days
      const days = Math.floor(diffInSeconds / 86400);
      return `${days}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div className="w-full flex flex-col">
      {/* Empty State */}
      {notes.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 px-4">
          <div className="p-4 rounded-full bg-indigo-50 dark:bg-indigo-900/20 mb-4">
            <BookOpenText className="h-8 w-8 text-indigo-500 dark:text-indigo-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No notes yet</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center mb-4">
            Start by creating your first language note
          </p>
          <Button
            className="bg-indigo-600 hover:bg-indigo-700 text-white"
            onClick={onCreateNote}
          >
            <Plus className="h-4 w-4 mr-2" />
            New Note
          </Button>
        </div>
      ) : (
        <div className="space-y-3 p-2">
          {notes.map((note) => {
            const noteConfig = NOTE_TYPE_CONFIG[note.note_type as keyof typeof NOTE_TYPE_CONFIG] || 
                               NOTE_TYPE_CONFIG.NOTE;
            const NoteIcon = noteConfig.icon;
            
            return (
              <Card
                key={note.id}
                className={`p-4 cursor-pointer transition-all hover:bg-gray-50 dark:hover:bg-gray-700/50 border border-gray-100 dark:border-gray-700 hover:shadow-md 
                  ${note.is_pinned ? 'border-l-4 border-l-indigo-500' : ''}
                  ${note.is_archived ? 'opacity-60' : ''}`}
                onClick={() => onNoteSelect(note)}
              >
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-full ${noteConfig.bgColor} flex-shrink-0`}>
                    <NoteIcon className={`h-4 w-4 ${noteConfig.color}`} />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start">
                      <h3 className="font-medium line-clamp-1 text-gray-900 dark:text-gray-100">{note.title}</h3>
                      <div className="flex items-center space-x-1 ml-2">
                        {note.is_pinned && (
                          <div className="w-2 h-2 rounded-full bg-indigo-500" title="Pinned" />
                        )}
                        {note.is_due_for_review && (
                          <div className="w-2 h-2 rounded-full bg-amber-500" title="Due for Review" />
                        )}
                      </div>
                    </div>
                    
                    {note.translation && (
                      <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-1 italic mt-1">
                        {note.translation}
                      </p>
                    )}
                    
                    <div className="flex flex-wrap items-center gap-x-3 mt-2 text-xs">
                      {note.language && (
                        <span className="text-gray-500 dark:text-gray-400 flex items-center gap-1">
                          <Languages className="h-3 w-3" />
                          {note.language.toUpperCase()}
                        </span>
                      )}
                      
                      {note.category_name && (
                        <span className="text-gray-500 dark:text-gray-400 truncate">
                          {note.category_name}
                        </span>
                      )}
                      
                      <span className="text-gray-400 dark:text-gray-500 ml-auto">
                        {formatRelativeTime(note.updated_at)}
                      </span>
                    </div>
                    
                    {/* Tags */}
                    {note.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {note.tags.slice(0, 3).map(tag => (
                          <span
                            key={tag.id}
                            className="px-1.5 py-0.5 rounded-full text-xs"
                            style={{ 
                              backgroundColor: `${tag.color}20`, 
                              color: tag.color 
                            }}
                          >
                            {tag.name}
                          </span>
                        ))}
                        {note.tags.length > 3 && (
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            +{note.tags.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            )
          })}
          
          {/* Create Note Button */}
          <div className="pt-2 pb-4">
            <Button
              variant="outline"
              className="w-full border border-dashed border-gray-300 dark:border-gray-600 hover:border-indigo-500 dark:hover:border-indigo-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition-all hover:shadow-md"
              onClick={onCreateNote}
            >
              <Plus className="h-4 w-4 mr-2" />
              Add New Note
            </Button>
          </div>
          
          {/* Pagination/Stats footer */}
          {notes.length > 0 && (
            <div className="text-xs text-gray-500 text-center py-2 border-t">
              {notes.length} note{notes.length !== 1 ? 's' : ''}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
