# backend/revision/models/revision_flashcard.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from authentication.models import User

class FlashcardDeck(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flashcard_decks')
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']), # Accelerate filtering by user and is_active
        ]
        unique_together = ['user', 'name'] # User can't have two decks with the same name

    def __str__(self):
        return f"{self.name} (by {self.user.username})"
    
    def get_card_count(self):
        return self.flashcards.count()
    
class Flashcard(models.Model):
    REVIEW_INTERVALS = {
        0: timedelta(days=1),  # Première révision
        1: timedelta(days=1),  # Après une révision
        2: timedelta(days=3),  # Après deux révisions
        3: timedelta(days=7),  # Après trois révisions
        4: timedelta(days=14), # Après quatre révisions
        5: timedelta(days=30), # Après cinq révisions
        # Pour les révisions suivantes, on utilise le dernier intervalle
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flashcards')
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
        indexes = [
            models.Index(fields=['user', 'deck']),  # Accélère les requêtes par utilisateur et deck
            models.Index(fields=['next_review']),   # Accélère les requêtes pour les cartes à réviser
        ]

    def __str__(self):
        return f"{self.front_text[:30]}... -> {self.back_text[:30]}... ({self.deck.name})"
    
    def mark_reviewed(self, success=True):
        """
        Marque la carte comme révisée et calcule la prochaine date de révision
        en fonction du succès et du nombre de révisions précédentes.
        
        Args:
            success (bool): Si True, la révision est considérée comme réussie.
        """
        self.last_reviewed = timezone.now()
        self.review_count += 1
        
        if success:
            # Implémentation de l'algorithme de répétition espacée
            interval_key = min(self.review_count, max(self.REVIEW_INTERVALS.keys()))
            interval = self.REVIEW_INTERVALS.get(interval_key, self.REVIEW_INTERVALS[max(self.REVIEW_INTERVALS.keys())])
            
            self.next_review = timezone.now() + interval
            self.learned = True
        else:
            # Si échec, réviser à nouveau dans 1 jour
            self.next_review = timezone.now() + timedelta(days=1)
            self.learned = False
        
        self.save()
    
    def reset_progress(self):
        """Réinitialise les statistiques de révision de la carte"""
        self.review_count = 0
        self.learned = False
        self.last_reviewed = None
        self.next_review = None
        self.save()