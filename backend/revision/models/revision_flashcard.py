# backend/revision/models/revision_flashcard.py
from django.db import models
from django.utils import timezone
from datetime import timedelta

class FlashcardDeck(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}"
    
class Flashcard(models.Model):
    deck = models.ForeignKey(FlashcardDeck, on_delete=models.CASCADE, related_name='flashcards')
    front_text = models.TextField()
    back_text = models.TextField()
    learned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    review_count = models.PositiveIntegerField(default=0)
    next_review = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['deck', '-created_at']

    def __str__(self):
        return f"{self.front_text} -> {self.back_text} - {self.deck.name}"
    
    def mark_reviewed(self, success=True):
        self.last_reviewed = timezone.now()
        self.review_count += 1
        
        if success:
            # Implement spaced repetition algorithm
            if self.review_count <= 1:
                interval = timedelta(days=1)
            elif self.review_count == 2:
                interval = timedelta(days=3)
            elif self.review_count == 3:
                interval = timedelta(days=7)
            else:
                interval = timedelta(days=14)
            
            self.next_review = timezone.now() + interval
            self.learned = True
        else:
            # If failed, review again in 1 day
            self.next_review = timezone.now() + timedelta(days=1)
            self.learned = False
        
        self.save()
