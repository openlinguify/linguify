// Continuation of src/app/(dashboard)/(apps)/notes/page.tsx
'use client';

import { useState } from 'react';
import { NoteList } from './_components/NoteList';
import { NoteEditor } from './_components/NoteEditor';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Note, Category } from '@/types/notebook';
import { notesApi } from '@/services/notebookAPI';
import { useToast } from "@/components/ui/use-toast";
import { Loader2 } from 'lucide-react';

export default function NotesPage() {
  const [selectedNote, setSelectedNote] = useState<Note | undefined>();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: notes = [], isLoading: isLoadingNotes } = useQuery({
    queryKey: ['notes'],
    queryFn: notesApi.getNotes,
  });

  const { data: categories = [], isLoading: isLoadingCategories } = useQuery({
    queryKey: ['categories'],
    queryFn: notesApi.getCategories,
  });

  const createNoteMutation = useMutation({
    mutationFn: notesApi.createNote,
    onSuccess: (newNote) => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
      setSelectedNote(newNote);
      toast({
        title: "Note created",
        description: "Your note has been created successfully.",
      });
    },
  });

  const updateNoteMutation = useMutation({
    mutationFn: notesApi.updateNote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
      toast({
        title: "Note updated",
        description: "Your changes have been saved.",
      });
    },
  });

  const deleteNoteMutation = useMutation({
    mutationFn: notesApi.deleteNote,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] });
      setSelectedNote(undefined);
      toast({
        title: "Note deleted",
        description: "The note has been deleted.",
      });
    },
  });

  const handleCreateNote = () => {
    createNoteMutation.mutate({ 
      title: 'New Note',
      content: '',
      note_type: 'NOTE',
      priority: 'MEDIUM'
    });
  };

  const handleSaveNote = async (noteData: Partial<Note>) => {
    if (selectedNote) {
      await updateNoteMutation.mutateAsync({
        id: selectedNote.id,
        ...noteData
      });
    }
  };

  const handleDeleteNote = async () => {
    if (selectedNote) {
      await deleteNoteMutation.mutateAsync(selectedNote.id);
    }
  };

  if (isLoadingNotes || isLoadingCategories) {
    return (
      <div className="h-[calc(100vh-4rem)] flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-4rem)] flex">
      {/* Sidebar with notes list */}
      <div className="w-96 border-r bg-gray-50">
        <NoteList
          notes={notes}
          onNoteSelect={setSelectedNote}
          onCreateNote={handleCreateNote}
        />
      </div>

      {/* Main content area */}
      <div className="flex-1">
        {selectedNote ? (
          <NoteEditor
            note={selectedNote}
            categories={categories}
            onSave={handleSaveNote}
            onDelete={handleDeleteNote}
          />
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500">
            <p>Select a note or create a new one</p>
          </div>
        )}
      </div>
    </div>
  );
}