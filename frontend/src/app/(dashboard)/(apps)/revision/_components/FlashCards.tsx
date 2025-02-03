import React, { useState, useEffect } from 'react';
import { useAuth } from '@/providers/AuthProvider';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Plus, Loader2, RefreshCw } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { revisionApi } from '@/services/revisionAPI';
import { Flashcard } from '@/types/revision';

interface FlashCardsProps {
  deckId: number;
}

interface FlashCardFormData {
  frontText: string;
  backText: string;
}

const FlashCards: React.FC<FlashCardsProps> = ({ deckId }) => {
  const { isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const [formData, setFormData] = useState<FlashCardFormData>({ frontText: '', backText: '' });
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchFlashcards = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await revisionApi.getFlashcards(deckId);
      setFlashcards(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      toast({
        title: 'Error',
        description: 'Unable to load flashcards',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && !isAuthLoading) {
      fetchFlashcards();
    }
  }, [isAuthenticated, isAuthLoading, deckId]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = (): boolean => {
    if (!formData.frontText.trim() || !formData.backText.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Both fields are required',
        variant: 'destructive',
      });
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      setIsSubmitting(true);
      setError(null);
      
      const newCard = await revisionApi.createFlashcard({
        front_text: formData.frontText.trim(),
        back_text: formData.backText.trim(),
        deck_id: deckId,
      });

      setFlashcards(prev => [...prev, newCard]);
      setFormData({ frontText: '', backText: '' });
      
      toast({
        title: 'Success',
        description: 'Flashcard created successfully',
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      toast({
        title: 'Error',
        description: 'Unable to create flashcard',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isAuthLoading) {
    return (
      <div className="flex items-center justify-center min-h-[200px]">
        <Loader2 className="h-8 w-8 animate-spin text-sky-600" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Card>
        <CardContent className="p-6">
          <Alert>
            <AlertDescription>
              Please log in to view and create flashcards.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="mb-4">
        <AlertDescription>{error}</AlertDescription>
        <Button onClick={fetchFlashcards} variant="outline" size="sm" className="mt-2">
          <RefreshCw className="w-4 h-4 mr-2" />
          Try again
        </Button>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Add Flashcard</CardTitle>
          <CardDescription>Create a new flashcard for your deck</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="frontText">Front</Label>
              <Input
                id="frontText"
                name="frontText"
                value={formData.frontText}
                onChange={handleInputChange}
                placeholder="Enter front text"
                disabled={isSubmitting}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="backText">Back</Label>
              <Input
                id="backText"
                name="backText"
                value={formData.backText}
                onChange={handleInputChange}
                placeholder="Enter back text"
                disabled={isSubmitting}
              />
            </div>
            <Button 
              type="submit" 
              disabled={isSubmitting}
              className="w-full"
            >
              {isSubmitting ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Plus className="w-4 h-4 mr-2" />
              )}
              Add flashcard
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <CardTitle>Your Flashcards</CardTitle>
        {isLoading ? (
          Array(3).fill(0).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3 mt-2" />
              </CardContent>
            </Card>
          ))
        ) : flashcards.length === 0 ? (
          <Card>
            <CardContent className="p-4 text-center text-muted-foreground">
              No flashcards yet. Create your first one above!
            </CardContent>
          </Card>
        ) : (
          flashcards.map((card) => (
            <Card key={card.id}>
              <CardContent className="p-4 flex justify-between items-center">
                <div>
                  <p className="font-medium">{card.front_text}</p>
                  <p className="text-muted-foreground mt-1">{card.back_text}</p>
                </div>
                {card.learned && (
                  <span className="text-green-500 text-sm font-medium">
                    Learned
                  </span>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default FlashCards;