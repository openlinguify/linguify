from django.db import models
from django.conf import settings
from django.utils import timezone
from .revision_flashcard import Flashcard
import uuid

class RevisionSession(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('MISSED', 'Missed'),
    ]

    session_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True,
        blank=True,
        help_text="ID unique de la session"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    flashcards = models.ManyToManyField(Flashcard, related_name='revision_sessions')
    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    success_rate = models.FloatField(null=True, blank=True)

    # Nouveaux champs pour le système de jalons
    total_cards = models.PositiveIntegerField(default=0)
    cards_completed = models.PositiveIntegerField(default=0)
    cards_correct = models.PositiveIntegerField(default=0)
    milestone_interval = models.PositiveIntegerField(default=7)
    last_milestone = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = 'revision'
        ordering = ['scheduled_date']

    def __str__(self):
        return f"Session for {self.user.username} on {self.scheduled_date}"

    def mark_completed(self, success_rate):
        self.status = 'COMPLETED'
        self.completed_date = timezone.now()
        self.success_rate = success_rate
        self.save()

    def check_overdue(self):
        if self.status == 'PENDING' and self.scheduled_date < timezone.now():
            self.status = 'MISSED'
            self.save()

    @property
    def progress_percentage(self):
        """Calcule le pourcentage de progression basé sur les cartes uniques étudiées"""
        if self.total_cards == 0:
            return 0
        # Compter les cartes uniques étudiées via les performances
        from .card_performance import CardPerformance
        unique_cards_studied = CardPerformance.objects.filter(
            user=self.user,
            card__in=self.flashcards.all(),
            created_at__gte=self.scheduled_date
        ).values('card').distinct().count()

        return int((unique_cards_studied / self.total_cards) * 100) if self.total_cards > 0 else 0

    @property
    def accuracy_rate(self):
        """Calcule le taux de réussite"""
        if self.cards_completed == 0:
            return 0
        return int((self.cards_correct / self.cards_completed) * 100)

    @property
    def cards_until_next_milestone(self):
        """Nombre de cartes restantes jusqu'au prochain jalon"""
        next_milestone = self.last_milestone + self.milestone_interval
        # Utiliser cards_completed (nombre de tentatives) pour les jalons
        remaining = next_milestone - self.cards_completed
        return max(0, remaining)

    @property
    def should_show_milestone(self):
        """Détermine si on doit afficher un jalon"""
        if self.cards_completed == 0:
            return False
        next_milestone = self.last_milestone + self.milestone_interval
        # Afficher jalon basé sur le nombre de tentatives, pas cartes uniques
        return self.cards_completed >= next_milestone and self.cards_completed > self.last_milestone

    def record_card_attempt(self, is_correct):
        """Enregistre une tentative de carte"""
        self.cards_completed += 1
        if is_correct:
            self.cards_correct += 1
        self.save(update_fields=['cards_completed', 'cards_correct'])

    def mark_milestone_shown(self):
        """Marque qu'un jalon a été affiché"""
        self.last_milestone = self.cards_completed
        self.save(update_fields=['last_milestone'])