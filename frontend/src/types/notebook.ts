// src/types/notes.ts
export interface Note {
    id: number;
    title: string;
    content: string;
    category?: number;
    category_name?: string;
    tags: Tag[];
    note_type: string;
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

  
  
  export interface Tag {
    id: number;
    name: string;
    color: string;
    notes_count: number;
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