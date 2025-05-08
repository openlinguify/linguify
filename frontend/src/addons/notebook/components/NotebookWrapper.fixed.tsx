"use client";

import React, { useState, useEffect } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
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
  Filter,
  Plus,
  Book,
  BookOpenText,
  Star,
  Clock,
  Languages,
  Bookmark,
  BookOpen,
  Template,
} from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import dynamic from "next/dynamic";
import { notebookAPI } from "@/addons/notebook/api/notebookAPI";
import { CategoryTree } from "./CategoryTree";
import { NoteList } from "./NoteList";
import { NoteEditor } from "./NoteEditor";

// Import rich text editor with dynamic loading (no SSR)
const Editor = dynamic(
  () => import("@/components/ui/Editor").then((mod) => mod.Editor),
  { ssr: false }
);
import { Category, Note } from "../types";
import { gradientText } from "@/styles/gradient_style";

export default function NotebookWrapper() {
  // State for notes, categories, and selected items
  const [notes, setNotes] = useState<Note[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | undefined>();
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  
  // State for UI elements
  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilter, setActiveFilter] = useState("all");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isTemplateDialogOpen, setIsTemplateDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
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

  // Search handler
  useEffect(() => {
    const searchNotes = async () => {
      if (searchTerm.trim()) {
        try {
          const searchResults = await notebookAPI.searchNotes(searchTerm);
          setNotes(searchResults);
        } catch (error) {
          console.error("Search failed:", error);
        }
      } else {
        refreshData();
      }
    };

    const debounce = setTimeout(searchNotes, 300);
    return () => clearTimeout(debounce);
  }, [searchTerm]);

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

  // Handle saving note
  const handleSaveNote = async (noteData: Partial<Note>) => {
    if (selectedNote) {
      try {
        await notebookAPI.updateNote(selectedNote.id, noteData);
        refreshData();
      } catch (error) {
        console.error("Failed to update note:", error);
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
        
        <div className="relative flex-1 max-w-md mx-4">
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
        
        <div className="flex items-center gap-2">
          <Dialog open={isTemplateDialogOpen} onOpenChange={setIsTemplateDialogOpen}>
            <DialogTrigger asChild>
              <Button 
                variant="outline" 
                className="border-indigo-200 hover:border-indigo-300 text-indigo-600 flex items-center gap-1"
              >
                <Template size={16} />
                <span className="hidden sm:inline">Templates</span>
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-3xl max-h-[80vh] overflow-auto">
              <DialogHeader>
                <DialogTitle className={`${gradientText} text-xl`}>Note Templates</DialogTitle>
              </DialogHeader>
              <div className="py-4 text-center">
                <p className="text-gray-500">Templates feature is coming soon!</p>
                <Button 
                  variant="outline" 
                  className="mt-4"
                  onClick={() => setIsTemplateDialogOpen(false)}
                >
                  Close
                </Button>
              </div>
            </DialogContent>
          </Dialog>
          
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
                  <Editor 
                    value={newNote.content}
                    onChange={(value) => setNewNote({ ...newNote, content: value })}
                    className="min-h-[200px]"
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
              className="h-7 w-7 p-0 rounded-full"
              title="Add category"
            >
              <Plus className="h-4 w-4 text-gray-500" />
            </Button>
          </div>
          
          <div className="overflow-auto flex-1">
            <CategoryTree 
              categories={categories} 
              selectedCategory={selectedCategory} 
              onSelect={handleCategorySelect}
            />
          </div>
          
          <div className="mt-4">
            <div className="bg-gray-50 dark:bg-gray-900/30 p-3 rounded-lg">
              <div className="text-xs text-gray-500 mb-2">QUICK LINKS</div>
              <div className="space-y-1">
                <div className="flex items-center p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer">
                  <Star className="h-4 w-4 text-yellow-500 mr-2" />
                  <span className="text-sm">Favorites</span>
                </div>
                <div className="flex items-center p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer">
                  <Clock className="h-4 w-4 text-blue-500 mr-2" />
                  <span className="text-sm">Recent Notes</span>
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