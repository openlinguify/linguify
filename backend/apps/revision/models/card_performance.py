# backend/apps/revision/models/card_performance.py
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class StudyMode(models.TextChoices):
    """Modes d'étude disponibles"""
    LEARN = 'learn', 'Apprendre'
    FLASHCARDS = 'flashcards', 'Flashcards'
    WRITE = 'write', 'Écrire'
    MATCH = 'match', 'Associer'
    REVIEW = 'review', 'Révision rapide'


class DifficultyLevel(models.TextChoices):
    """Niveau de difficulté de la réponse"""
    EASY = 'easy', 'Facile'
    MEDIUM = 'medium', 'Moyen'
    HARD = 'hard', 'Difficile'
    WRONG = 'wrong', 'Incorrect'


class CardPerformance(models.Model):
    """
    Modèle pour tracker la performance détaillée d'une carte dans différents modes d'étude.
    Permet un algorithme adaptatif qui ajuste le statut "learned" basé sur les performances réelles.
    """
    card = models.ForeignKey(
        'revision.Flashcard',
        on_delete=models.CASCADE,
        related_name='performances'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='card_performances'
    )
    study_mode = models.CharField(
        max_length=20,
        choices=StudyMode.choices,
        help_text="Mode d'étude dans lequel la performance a été enregistrée"
    )
    difficulty = models.CharField(
        max_length=10,
        choices=DifficultyLevel.choices,
        help_text="Difficulté perçue par l'utilisateur"
    )
    response_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Temps de réponse en secondes"
    )
    was_correct = models.BooleanField(
        default=True,
        help_text="Si la réponse était correcte"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True
    )

    # Métadonnées additionnelles
    session_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID de session pour grouper les performances d'une même session d'étude"
    )
    confidence_before = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score de confiance avant cette performance"
    )
    confidence_after = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score de confiance après cette performance"
    )

    class Meta:
        app_label = 'revision'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['card', 'study_mode', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['card', '-created_at']),
            models.Index(fields=['study_mode', '-created_at']),
        ]

    def __str__(self):
        return f"{self.card.front_text[:30]} - {self.study_mode} - {self.difficulty} ({self.created_at.strftime('%Y-%m-%d')})"

    @property
    def score_impact(self):
        """
        Calcule l'impact de cette performance sur le score de confiance.

        Returns:
            int: Impact sur le score (-30 à +15)
        """
        if not self.was_correct:
            return -30  # Forte pénalité pour réponse incorrecte

        difficulty_impact = {
            DifficultyLevel.EASY: 15,
            DifficultyLevel.MEDIUM: 8,
            DifficultyLevel.HARD: 3,
            DifficultyLevel.WRONG: -30
        }
        return difficulty_impact.get(self.difficulty, 5)


class CardMastery(models.Model):
    """
    Modèle pour stocker le niveau de maîtrise agrégé d'une carte.
    Calculé en temps réel basé sur les performances dans tous les modes.
    """
    card = models.OneToOneField(
        'revision.Flashcard',
        on_delete=models.CASCADE,
        related_name='mastery',
        primary_key=True
    )
    confidence_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score de confiance global (0-100)"
    )

    # Scores par mode d'étude
    learn_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Taux de réussite en mode Apprendre (0.0-1.0)"
    )
    flashcards_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Taux de réussite en mode Flashcards (0.0-1.0)"
    )
    write_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Taux de réussite en mode Écrire (0.0-1.0)"
    )
    match_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Taux de réussite en mode Associer (0.0-1.0)"
    )
    review_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Taux de réussite en mode Révision (0.0-1.0)"
    )

    # Dates de dernière pratique par mode
    last_learn = models.DateTimeField(null=True, blank=True)
    last_flashcards = models.DateTimeField(null=True, blank=True)
    last_write = models.DateTimeField(null=True, blank=True)
    last_match = models.DateTimeField(null=True, blank=True)
    last_review = models.DateTimeField(null=True, blank=True)

    # Compteurs
    total_attempts = models.PositiveIntegerField(default=0)
    successful_attempts = models.PositiveIntegerField(default=0)

    # Métadonnées
    updated_at = models.DateTimeField(auto_now=True)

    # Statut dérivé
    mastery_level = models.CharField(
        max_length=20,
        choices=[
            ('learning', 'En apprentissage'),
            ('reviewing', 'En révision'),
            ('mastered', 'Maîtrisé'),
            ('struggling', 'En difficulté')
        ],
        default='learning',
        help_text="Niveau de maîtrise calculé automatiquement"
    )

    class Meta:
        app_label = 'revision'
        verbose_name = 'Card Mastery'
        verbose_name_plural = 'Card Masteries'

    def __str__(self):
        return f"{self.card.front_text[:30]} - Confidence: {self.confidence_score}% - {self.mastery_level}"

    def calculate_confidence_score(self):
        """
        Calcule le score de confiance basé sur les performances dans tous les modes.

        Algorithme:
        - Prend en compte les scores de tous les modes avec pondération
        - Le mode "Learn" a plus de poids car c'est le mode d'apprentissage initial
        - Les performances récentes ont plus de poids que les anciennes
        """
        # Pondération par mode (total = 1.0)
        weights = {
            'learn': 0.35,        # Mode d'apprentissage principal
            'flashcards': 0.25,   # Important pour la mémorisation
            'write': 0.20,        # Test actif de rappel
            'match': 0.10,        # Reconnaissance
            'review': 0.10        # Révision espacée
        }

        # Calculer le score pondéré
        weighted_score = (
            self.learn_score * weights['learn'] +
            self.flashcards_score * weights['flashcards'] +
            self.write_score * weights['write'] +
            self.match_score * weights['match'] +
            self.review_score * weights['review']
        ) * 100

        # Ajuster en fonction du nombre total de tentatives
        # Plus il y a de données, plus le score est fiable
        if self.total_attempts < 3:
            weighted_score *= 0.7  # Réduire la confiance si peu de données
        elif self.total_attempts < 5:
            weighted_score *= 0.85

        return int(max(0, min(100, weighted_score)))

    def update_mastery_level(self):
        """
        Met à jour le niveau de maîtrise basé sur le score de confiance
        et la cohérence des performances entre les modes.
        """
        score = self.confidence_score

        # Calculer la variance entre les modes (cohérence)
        scores = [
            self.learn_score, self.flashcards_score,
            self.write_score, self.match_score, self.review_score
        ]
        non_zero_scores = [s for s in scores if s > 0]

        if not non_zero_scores:
            self.mastery_level = 'learning'
        elif score >= 85 and len(non_zero_scores) >= 3:
            # Maîtrisé si score élevé et testé dans plusieurs modes
            self.mastery_level = 'mastered'
        elif score >= 70:
            # En révision si score correct
            self.mastery_level = 'reviewing'
        elif score < 40 and self.total_attempts >= 3:
            # En difficulté si score faible après plusieurs tentatives
            self.mastery_level = 'struggling'
        else:
            # En apprentissage par défaut
            self.mastery_level = 'learning'

        self.save(update_fields=['mastery_level', 'updated_at'])

    def should_be_learned(self):
        """
        Détermine si la carte devrait être marquée comme "learned" (apprise).

        Returns:
            bool: True si la carte devrait être marquée comme apprise
        """
        return (
            self.confidence_score >= 85 and
            self.mastery_level == 'mastered' and
            self.total_attempts >= 5
        )

    def should_be_reviewed(self):
        """
        Détermine si la carte devrait être marquée comme "to review" (à réviser).

        Returns:
            bool: True si la carte devrait être marquée comme à réviser
        """
        return (
            self.confidence_score < 70 or
            self.mastery_level == 'struggling' or
            (self.mastery_level == 'reviewing' and self.confidence_score < 75)
        )

    @classmethod
    def update_from_performance(cls, performance):
        """
        Met à jour ou crée le CardMastery basé sur une nouvelle performance.

        Args:
            performance (CardPerformance): La performance à intégrer
        """
        mastery, created = cls.objects.get_or_create(card=performance.card)

        # Enregistrer le score avant
        performance.confidence_before = mastery.confidence_score

        # Mettre à jour les compteurs
        mastery.total_attempts += 1
        if performance.was_correct:
            mastery.successful_attempts += 1

        # Mettre à jour la date de dernière pratique pour ce mode
        mode_field = f"last_{performance.study_mode}"
        if hasattr(mastery, mode_field):
            setattr(mastery, mode_field, performance.created_at)

        # Recalculer le score pour ce mode spécifique
        # Exclure la performance actuelle de la requête si elle est déjà sauvegardée
        recent_performances = list(CardPerformance.objects.filter(
            card=performance.card,
            study_mode=performance.study_mode
        ).order_by('-created_at')[:10])

        if recent_performances:
            correct_count = sum(1 for p in recent_performances if p.was_correct)
            mode_score = correct_count / len(recent_performances)
            score_field = f"{performance.study_mode}_score"
            if hasattr(mastery, score_field):
                setattr(mastery, score_field, mode_score)

        # Recalculer le score de confiance global
        mastery.confidence_score = mastery.calculate_confidence_score()

        # Mettre à jour le niveau de maîtrise (déjà sauvegarde avec update_fields)
        mastery.update_mastery_level()

        # Sauvegarder toutes les modifications du mastery
        # (update_mastery_level a déjà sauvegardé mastery_level et updated_at)
        # On sauvegarde les autres champs modifiés
        update_fields = [
            'total_attempts', 'successful_attempts',
            'confidence_score'
        ]

        # Ajouter les champs de mode seulement s'ils existent
        score_field = f"{performance.study_mode}_score"
        if hasattr(mastery, mode_field):
            update_fields.append(mode_field)
        if hasattr(mastery, score_field):
            update_fields.append(score_field)

        mastery.save(update_fields=update_fields)

        # Enregistrer le score après dans la performance
        performance.confidence_after = mastery.confidence_score
        performance.save(update_fields=['confidence_before', 'confidence_after'])

        # Mettre à jour le statut "learned" de la carte
        if mastery.should_be_learned() and not performance.card.learned:
            performance.card.learned = True
            performance.card.save(update_fields=['learned'])
        elif mastery.should_be_reviewed() and performance.card.learned:
            performance.card.learned = False
            performance.card.save(update_fields=['learned'])

        return mastery