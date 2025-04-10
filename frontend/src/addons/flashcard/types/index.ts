// src/addons/flashcard/types/index.ts

export interface SearchParams {
    search?: string;
    username?: string;
    sort_by?: 'popularity' | 'recent' | 'alphabetical';
    public?: boolean;
    mine?: boolean;
    archived?: boolean;
    limit?: number;
}
export interface FlashcardDeck {
    id: number;
    name: string;
    description: string;
    created_at: string;
    updated_at: string;
    is_active: boolean;
    user?: any;
    card_count?: number;
    learned_count?: number;
    cards?: Flashcard[];
    is_public?: boolean;
    username?: string;
    is_archived?: boolean;
    is_cloned?: boolean;
    is_cloning?: boolean;
    is_cloning_error?: boolean;
    deck: number;
    front_text: string;
    back_text: string;
    learned: boolean;
    last_reviewed: string | null;
    review_count: number;
    next_review: string | null;
 
  }
  
  export interface FlashcardAppProps {
    selectedDeck: FlashcardDeck;
    onCardUpdate: () => void;
  }
  
  export interface Flashcard {
    id: number;
    deck: number;
    front_text: string;
    back_text: string;
    learned: boolean;
    created_at: string;
    updated_at: string;
    last_reviewed: string | null;
    review_count: number;
    next_review: string | null;
  }