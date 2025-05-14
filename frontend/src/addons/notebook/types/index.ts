// src/types/notes.ts
import { TagItem } from "../components/TagManager";

export interface Note {
  id: number;
  title: string;
  content: string;
  language: string;
  difficulty?: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
  category?: number;
  category_name?: string;
  tags?: TagItem[];
  related_words: string[];
  translation?: string;
  pronunciation?: string;
  example_sentences: string[];
  note_type: 'VOCABULARY' | 'GRAMMAR' | 'EXPRESSION' | 'CULTURE' | 'NOTE' | 'TASK' | 'REMINDER' | 'MEETING' | 'IDEA' | 'PROJECT' | 'EVENT' | 'TEXT' | 'IMAGE' | 'VIDEO';
  created_at: string;
  updated_at: string;
  last_reviewed_at?: string;
  review_count: number;
  is_pinned: boolean;
  is_archived: boolean;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  is_shared: boolean;
  is_due_for_review: boolean;
  time_until_review?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface CursorPaginatedResponse<T> {
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface NotebookClientProps {
  searchTerm?: string;
  filter?: string;
}

export interface NoteEditorProps {
  note?: Note;
  categories: Category[];
  onSave: (note: Partial<Note>) => Promise<void>;
  onDelete?: () => Promise<void>;
}

export interface CategoryTreeProps {
  categories: Category[];
  selectedCategory?: number;
  onSelect: (categoryId: number) => void;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
  parent?: number;
  parent_name?: string;
  created_at: string;
  subcategories: Category[];
  notes_count: number;
  notes: Note[];
}