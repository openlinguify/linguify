// src/components/notes/NoteEditor.tsx
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Loader2, Save, Pin, Archive, Trash2, Clock, Languages, 
  Volume2, Plus, X, Bookmark, Type
} from "lucide-react";
import { Tag, Category } from "@/addons/notebook/types";
import dynamic from "next/dynamic";
import { NoteEditorProps } from "@/addons/notebook/types/";
import useSpeechSynthesis from '@/core/speech/useSpeechSynthesis';
import { notebookAPI } from "../api/notebookAPI";

// Import Editor directly for debugging
import { Editor as StaticEditor } from "@/components/ui/Editor";

const Editor = dynamic(
  () => import("@/components/ui/Editor").then((mod) => mod.Editor),
  { ssr: false }
);

const LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'fr', label: 'French' },
  { value: 'es', label: 'Spanish' },
  { value: 'de', label: 'German' },
  { value: 'it', label: 'Italian' },
  { value: 'pt', label: 'Portuguese' },
  { value: 'nl', label: 'Dutch' },
  { value: 'ru', label: 'Russian' },
  { value: 'zh', label: 'Chinese' },
  { value: 'ja', label: 'Japanese' },
  { value: 'ko', label: 'Korean' },
  { value: 'ar', label: 'Arabic' },
];

const DIFFICULTY_OPTIONS = [
  { value: 'BEGINNER', label: 'Beginner' },
  { value: 'INTERMEDIATE', label: 'Intermediate' },
  { value: 'ADVANCED', label: 'Advanced' },
];

export function NoteEditor({
  note,
  categories,
  onSave,
  onDelete,
}: NoteEditorProps) {
  // Basic note fields
  const [title, setTitle] = useState(note?.title || "");
  const [content, setContent] = useState(note?.content || "");
  const [category, setCategory] = useState<number | undefined>(note?.category);
  const [selectedTags, setSelectedTags] = useState<Tag[]>(note?.tags || []);
  const [noteType, setNoteType] = useState(note?.note_type || "VOCABULARY");
  const [priority, setPriority] = useState(note?.priority || "MEDIUM");
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  
  // Language learning specific fields
  const [language, setLanguage] = useState(note?.language || "fr");
  const [translation, setTranslation] = useState(note?.translation || "");
  const [pronunciation, setPronunciation] = useState(note?.pronunciation || "");
  const [difficulty, setDifficulty] = useState(note?.difficulty || "INTERMEDIATE");
  const [exampleSentences, setExampleSentences] = useState<string[]>(note?.example_sentences || []);
  const [relatedWords, setRelatedWords] = useState<string[]>(note?.related_words || []);
  const [newSentence, setNewSentence] = useState("");
  const [newRelatedWord, setNewRelatedWord] = useState("");

  // Tab state
  const [activeTab, setActiveTab] = useState("content");

  // Speech synthesis
  const { speak, speaking, voices } = useSpeechSynthesis();

  // Available tags
  const [availableTags, setAvailableTags] = useState<Tag[]>([]);
  const [newTagName, setNewTagName] = useState("");
  const [newTagColor, setNewTagColor] = useState("#3B82F6");

  useEffect(() => {
    const fetchTags = async () => {
      try {
        const tags = await notebookAPI.getTags();
        setAvailableTags(tags);
      } catch (error) {
        console.error("Failed to fetch tags:", error);
      }
    };

    fetchTags();
  }, []);

  useEffect(() => {
    if (note) {
      setTitle(note.title);
      setContent(note.content);
      setCategory(note.category);
      setSelectedTags(note.tags || []);
      setNoteType(note.note_type);
      setPriority(note.priority);
      
      // Set language learning fields
      setLanguage(note.language || "fr");
      setTranslation(note.translation || "");
      setPronunciation(note.pronunciation || "");
      setDifficulty(note.difficulty || "INTERMEDIATE");
      setExampleSentences(note.example_sentences || []);
      setRelatedWords(note.related_words || []);
    }
  }, [note]);

  // Cette fonction vérifie si l'éditeur est vide, même s'il contient des nœuds vides
  const isEditorEmpty = (editorContent: string) => {
    // Si le contenu est vide ou null
    if (!editorContent) return true;
    
    // Si le contenu est juste des balises HTML sans texte
    const div = document.createElement('div');
    div.innerHTML = editorContent;
    const textContent = div.textContent?.trim();
    
    return !textContent || textContent === '';
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Vérifier si le titre est vide
      if (!title.trim()) {
        alert("Le titre ne peut pas être vide");
        setIsSaving(false);
        return;
      }
      
      // Vérifier si l'éditeur a du contenu
      const editorIsEmpty = isEditorEmpty(content);
      
      // Préparer le contenu de manière plus robuste
      const contentToSave = editorIsEmpty ? "" : content;
      
      // Feedback visuel pour l'utilisateur
      const saveStartTime = Date.now();
      
      // Créer l'objet de données à sauvegarder
      const noteData = {
        ...(note || {}),
        id: note?.id, // Make sure we keep the ID for updating
        title: title.trim(),
        content: contentToSave,
        category,
        tags: selectedTags || [],
        note_type: noteType || "VOCABULARY",
        priority: priority || "MEDIUM",
        language: language || "fr",
        translation: translation || "",
        pronunciation: pronunciation || "",
        difficulty: difficulty || "INTERMEDIATE",
        example_sentences: exampleSentences || [],
        related_words: relatedWords || []
      };
      
      // Sauvegarder la note
      await onSave(noteData);
      
      // Assurer un minimum de temps pour le feedback visuel (au moins 500ms)
      const elapsedTime = Date.now() - saveStartTime;
      if (elapsedTime < 500) {
        await new Promise(resolve => setTimeout(resolve, 500 - elapsedTime));
      }
      
    } catch (error) {
      console.error("Save error:", error);
      alert("Une erreur est survenue lors de la sauvegarde. Veuillez réessayer.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (
      !onDelete ||
      !window.confirm("Are you sure you want to delete this note?")
    ) {
      return;
    }
    setIsDeleting(true);
    try {
      await onDelete();
    } finally {
      setIsDeleting(false);
    }
  };

  const handleAddSentence = () => {
    if (newSentence.trim()) {
      setExampleSentences([...exampleSentences, newSentence.trim()]);
      setNewSentence("");
    }
  };

  const handleRemoveSentence = (index: number) => {
    setExampleSentences(
      exampleSentences.filter((_, i) => i !== index)
    );
  };

  const handleAddRelatedWord = () => {
    if (newRelatedWord.trim()) {
      setRelatedWords([...relatedWords, newRelatedWord.trim()]);
      setNewRelatedWord("");
    }
  };

  const handleRemoveRelatedWord = (index: number) => {
    setRelatedWords(
      relatedWords.filter((_, i) => i !== index)
    );
  };

  const handleSpeak = (text: string) => {
    const langVoice = voices.find(v => v.lang.startsWith(language));
    speak(text, langVoice);
  };

  const handleToggleTag = (tag: Tag) => {
    const isSelected = selectedTags.some(t => t.id === tag.id);
    if (isSelected) {
      setSelectedTags(selectedTags.filter(t => t.id !== tag.id));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };

  const handleCreateTag = async () => {
    if (!newTagName.trim()) return;
    
    try {
      const newTag = await notebookAPI.createTag({
        name: newTagName,
        color: newTagColor
      });
      setAvailableTags([...availableTags, newTag]);
      setSelectedTags([...selectedTags, newTag]);
      setNewTagName("");
    } catch (error) {
      console.error("Failed to create tag:", error);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="border-b p-4 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Note title"
            className="text-lg font-medium w-72"
          />

          <Select 
            value={language} 
            onValueChange={setLanguage}
          >
            <SelectTrigger className="w-36">
              <Languages className="h-4 w-4 mr-2" />
              <SelectValue placeholder="Language" />
            </SelectTrigger>
            <SelectContent>
              {LANGUAGE_OPTIONS.map(option => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select 
            value={category?.toString() || "none"} 
            onValueChange={(value) => setCategory(value !== "none" ? Number(value) : undefined)}
          >
            <SelectTrigger className="w-40">
              <Bookmark className="h-4 w-4 mr-2" />
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">No category</SelectItem>
              {categories.map((cat) => (
                <SelectItem key={cat.id} value={cat.id.toString()}>
                  {cat.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select 
            value={difficulty} 
            onValueChange={setDifficulty}
          >
            <SelectTrigger className="w-40">
              <Type className="h-4 w-4 mr-2" />
              <SelectValue placeholder="Difficulty" />
            </SelectTrigger>
            <SelectContent>
              {DIFFICULTY_OPTIONS.map(option => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          {note && (
            <>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onSave({ ...note, is_pinned: !note.is_pinned })}
              >
                <Pin
                  className={`h-4 w-4 ${note.is_pinned ? "text-blue-500" : ""}`}
                />
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={() =>
                  onSave({ ...note, is_archived: !note.is_archived })
                }
              >
                <Archive
                  className={`h-4 w-4 ${
                    note.is_archived ? "text-gray-500" : ""
                  }`}
                />
              </Button>

              {note.is_due_for_review && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() =>
                    onSave({
                      ...note,
                      last_reviewed_at: new Date().toISOString(),
                      review_count: note.review_count + 1
                    })
                  }
                >
                  <Clock className="h-4 w-4 text-orange-500" />
                </Button>
              )}
            </>
          )}

          <Button onClick={handleSave} disabled={isSaving}>
            {isSaving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Save
          </Button>

          {note && onDelete && (
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              {isDeleting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList className="mx-4 mt-2">
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="language">Language Learning</TabsTrigger>
          <TabsTrigger value="examples">Examples</TabsTrigger>
          <TabsTrigger value="tags">Tags</TabsTrigger>
        </TabsList>

        <TabsContent value="content" className="flex-1 overflow-auto p-4">
          <Editor
            value={content}
            onChange={setContent}
            className="min-h-[500px]"
          />
        </TabsContent>

        <TabsContent value="language" className="p-4 space-y-4">
          {/* Language learning features */}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Translation</label>
              <div className="flex items-center">
                <Textarea
                  value={translation}
                  onChange={(e) => setTranslation(e.target.value)}
                  placeholder="Translation in your native language"
                  className="flex-1"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Pronunciation</label>
              <div className="flex items-center gap-2">
                <Input
                  value={pronunciation}
                  onChange={(e) => setPronunciation(e.target.value)}
                  placeholder="Pronunciation guide"
                  className="flex-1"
                />
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleSpeak(title)}
                  disabled={speaking}
                >
                  <Volume2 className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="space-y-2 md:col-span-2">
              <label className="text-sm font-medium">Related Words</label>
              <div className="flex items-center gap-2">
                <Input
                  value={newRelatedWord}
                  onChange={(e) => setNewRelatedWord(e.target.value)}
                  placeholder="Add related word"
                  className="flex-1"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleAddRelatedWord();
                    }
                  }}
                />
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={handleAddRelatedWord}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                {relatedWords.map((word, index) => (
                  <div 
                    key={index}
                    className="bg-gray-100 px-3 py-1 rounded-full flex items-center gap-1"
                  >
                    <span>{word}</span>
                    <button
                      className="text-gray-500 hover:text-gray-700"
                      onClick={() => handleRemoveRelatedWord(index)}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
                {relatedWords.length === 0 && (
                  <div className="text-gray-400 text-sm">No related words added</div>
                )}
              </div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="examples" className="p-4 space-y-4">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Example Sentences</label>
              <div className="flex items-center gap-2">
                <Textarea
                  value={newSentence}
                  onChange={(e) => setNewSentence(e.target.value)}
                  placeholder="Add example sentence"
                  className="flex-1"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && e.ctrlKey) {
                      handleAddSentence();
                    }
                  }}
                />
                <div className="flex flex-col gap-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={handleAddSentence}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                  {newSentence && (
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleSpeak(newSentence)}
                      disabled={speaking}
                    >
                      <Volume2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
              <div className="text-xs text-gray-500">
                Press Ctrl+Enter to add quickly
              </div>
            </div>

            <div className="space-y-2">
              {exampleSentences.map((sentence, index) => (
                <div 
                  key={index}
                  className="bg-gray-50 p-3 rounded-md flex justify-between items-start"
                >
                  <div className="flex-1">{sentence}</div>
                  <div className="flex items-center gap-1 ml-2">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleSpeak(sentence)}
                      disabled={speaking}
                    >
                      <Volume2 className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleRemoveSentence(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
              {exampleSentences.length === 0 && (
                <div className="text-center py-8 text-gray-400">
                  No example sentences added yet
                </div>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="tags" className="p-4 space-y-4">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Create New Tag</label>
              <div className="flex items-center gap-2">
                <Input
                  value={newTagName}
                  onChange={(e) => setNewTagName(e.target.value)}
                  placeholder="Tag name"
                  className="flex-1"
                />
                <input
                  type="color"
                  value={newTagColor}
                  onChange={(e) => setNewTagColor(e.target.value)}
                  className="h-9 w-12 border rounded p-1"
                />
                <Button 
                  variant="outline" 
                  onClick={handleCreateTag}
                >
                  Create Tag
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Select Tags</label>
              <div className="flex flex-wrap gap-2">
                {availableTags.map(tag => (
                  <div
                    key={tag.id}
                    onClick={() => handleToggleTag(tag)}
                    className={`
                      px-3 py-1 rounded-full cursor-pointer text-sm
                      ${selectedTags.some(t => t.id === tag.id) 
                        ? 'bg-blue-100 text-blue-800 border-blue-200 border'
                        : 'bg-gray-100 text-gray-800 hover:bg-gray-200'}
                    `}
                  >
                    {tag.name}
                  </div>
                ))}
                {availableTags.length === 0 && (
                  <div className="text-gray-400 text-sm">No tags available</div>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Selected Tags</label>
              <div className="flex flex-wrap gap-2">
                {selectedTags.map(tag => (
                  <div
                    key={tag.id}
                    className="px-3 py-1 rounded-full flex items-center gap-1"
                    style={{ 
                      backgroundColor: `${tag.color}20`,
                      color: tag.color 
                    }}
                  >
                    <span>{tag.name}</span>
                    <button
                      className="hover:text-red-500"
                      onClick={() => handleToggleTag(tag)}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
                {selectedTags.length === 0 && (
                  <div className="text-gray-400 text-sm">No tags selected</div>
                )}
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}