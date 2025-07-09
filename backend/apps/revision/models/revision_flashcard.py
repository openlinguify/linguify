# backend/revision/models/revision_flashcard.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from apps.authentication.models import User

class FlashcardDeck(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='flashcard_decks')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False) 
    is_archived = models.BooleanField(default=False)
    expiration_date = models.DateTimeField(null=True, blank=True)
    
    # Nouveaux paramètres d'apprentissage
    required_reviews_to_learn = models.PositiveIntegerField(
        default=3,
        help_text="Nombre de révisions correctes nécessaires pour marquer une carte comme apprise"
    )
    auto_mark_learned = models.BooleanField(
        default=True,
        help_text="Marquer automatiquement les cartes comme apprises après X révisions"
    )
    reset_on_wrong_answer = models.BooleanField(
        default=False,
        help_text="Remettre le compteur à zéro si mauvaise réponse"
    )
    
    # Constante de classe pour la période d'avertissement (en jours)
    WARNING_THRESHOLD_DAYS = 3
    # Constante pour la durée d'archivage avant expiration auto
    DEFAULT_EXPIRATION_DAYS = 30

    class Meta:
        app_label = 'revision'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['is_public']),
            models.Index(fields=['is_archived']),
            models.Index(fields=['expiration_date']),  # Nouvel index pour les requêtes d'expiration
        ]
        unique_together = ['user', 'name'] 

    def __str__(self):
        return f"{self.name} (by {self.user.username})"
    
    def archive(self):
        """
        Archive ce deck et définit sa date d'expiration automatique.
        Les decks archivés sont supprimés automatiquement après la période d'expiration.
        """
        self.is_archived = True
        # Définir automatiquement l'expiration à 30 jours lors de l'archivage
        self.set_expiration(days=self.DEFAULT_EXPIRATION_DAYS)
        self.save(update_fields=['is_archived', 'expiration_date', 'updated_at'])
        return self.get_days_until_deletion()
        
    def unarchive(self):
        """
        Retire le deck des archives et annule son expiration automatique
        """
        self.is_archived = False
        self.expiration_date = None  # Annuler l'expiration
        self.save(update_fields=['is_archived', 'expiration_date', 'updated_at'])
    
    def set_expiration(self, days=DEFAULT_EXPIRATION_DAYS):
        """
        Définit une date d'expiration pour ce deck.
        
        Args:
            days (int): Nombre de jours avant expiration
        """
        self.expiration_date = timezone.now() + timedelta(days=days)
        self.save(update_fields=['expiration_date'])

    @property
    def is_expired(self):
        """
        Vérifie si un deck est expiré ET archivé.
        Les decks ne sont considérés comme expirés que s'ils sont aussi archivés.
        """
        if not self.expiration_date or not self.is_archived:
            return False
        return timezone.now() > self.expiration_date
    
    def get_days_until_deletion(self):
        """
        Calcule le nombre de jours restants avant la suppression du deck.
        
        Returns:
            int|None: Nombre de jours avant suppression ou None si pas d'expiration
        """
        if not self.expiration_date or not self.is_archived:
            return None
            
        days = (self.expiration_date - timezone.now()).days
        return max(0, days)  # Retourne au minimum 0 (expiration aujourd'hui)
    
    @property
    def deletion_date(self):
        """
        Retourne la date de suppression prévue si archivé et expiré.
        
        Returns:
            datetime|None: Date de suppression ou None si pas d'expiration/archivage
        """
        if not self.expiration_date or not self.is_archived:
            return None
        return self.expiration_date
    
    @property
    def expiration_warning(self):
        """
        Vérifie si le deck approche de sa date d'expiration.
        
        Returns:
            bool: True si le deck sera supprimé dans WARNING_THRESHOLD_DAYS jours ou moins
        """
        days_left = self.get_days_until_deletion()
        if days_left is None:
            return False
        return days_left <= self.WARNING_THRESHOLD_DAYS and days_left > 0
    
    @property
    def expiration_status(self):
        """
        Renvoie des informations détaillées sur l'état d'expiration.
        
        Returns:
            dict: Informations sur l'expiration
        """
        days_left = self.get_days_until_deletion()
        
        if not self.is_archived:
            return {
                'is_archived': False,
                'will_expire': False,
                'message': "Ce deck n'est pas archivé et ne sera pas supprimé automatiquement."
            }
            
        if days_left is None:
            return {
                'is_archived': True,
                'will_expire': False,
                'message': "Ce deck est archivé mais n'a pas de date d'expiration."
            }
            
        if days_left <= 0:
            return {
                'is_archived': True,
                'will_expire': True,
                'days_left': 0,
                'expiration_date': self.expiration_date,
                'needs_warning': False,
                'message': "Ce deck est expiré et sera supprimé lors du prochain nettoyage."
            }
            
        return {
            'is_archived': True,
            'will_expire': True,
            'days_left': days_left,
            'expiration_date': self.expiration_date,
            'needs_warning': days_left <= self.WARNING_THRESHOLD_DAYS,
            'message': f"Ce deck sera supprimé dans {days_left} jours (le {self.expiration_date.strftime('%d/%m/%Y')})."
        }

    @classmethod
    def cleanup_expired(cls):
        """
        Supprime les decks qui sont à la fois expirés ET archivés
        
        Returns:
            int: Nombre de decks supprimés
        """
        expired = cls.objects.filter(
            expiration_date__isnull=False,
            expiration_date__lt=timezone.now(),
            is_archived=True  # Uniquement les decks archivés
        )
        count = expired.count()
        
        # Log des decks qui vont être supprimés
        for deck in expired:
            print(f"Suppression du deck expiré: '{deck.name}' (ID: {deck.id}) - Archivé le {deck.updated_at}")
            
        expired.delete()
        return count
    
    @classmethod
    def get_decks_needing_warning(cls, user=None):
        """
        Récupère tous les decks qui approchent de leur date d'expiration
        et nécessitent un avertissement.
        
        Args:
            user (User, optional): Filtrer par utilisateur spécifique
            
        Returns:
            QuerySet: Decks nécessitant un avertissement
        """
        warning_date = timezone.now() + timedelta(days=cls.WARNING_THRESHOLD_DAYS)
        
        query = cls.objects.filter(
            is_archived=True,
            expiration_date__isnull=False,
            expiration_date__lte=warning_date,
            expiration_date__gt=timezone.now()
        )
        
        if user:
            query = query.filter(user=user)
            
        return query.order_by('expiration_date')
    
    @classmethod
    def extend_expiration(cls, deck_id, days=DEFAULT_EXPIRATION_DAYS):
        """
        Prolonge la durée d'expiration d'un deck.
        
        Args:
            deck_id (int): ID du deck à prolonger
            days (int, optional): Nombre de jours supplémentaires
            
        Returns:
            dict: Informations sur la nouvelle date d'expiration
        """
        try:
            deck = cls.objects.get(id=deck_id)
            
            # Si le deck n'a pas de date d'expiration, en définir une
            if not deck.expiration_date:
                deck.set_expiration(days)
            else:
                # Sinon, ajouter des jours à la date existante
                deck.expiration_date = deck.expiration_date + timedelta(days=days)
                deck.save(update_fields=['expiration_date'])
                
            return {
                'success': True,
                'deck_id': deck_id,
                'deck_name': deck.name,
                'new_expiration': deck.expiration_date,
                'days_added': days,
                'days_until_deletion': deck.get_days_until_deletion()
            }
        except cls.DoesNotExist:
            return {
                'success': False,
                'error': f"Deck avec ID {deck_id} introuvable"
            }
    
    def get_learning_presets(self):
        """Retourne les presets prédéfinis de configuration d'apprentissage"""
        return {
            'beginner': {
                'required_reviews_to_learn': 2,
                'auto_mark_learned': True,
                'reset_on_wrong_answer': False,
                'name': "Débutant - Apprentissage rapide",
                'description': "Idéal pour débuter, carte apprise après 2 révisions correctes"
            },
            'normal': {
                'required_reviews_to_learn': 3,
                'auto_mark_learned': True,
                'reset_on_wrong_answer': False,
                'name': "Normal - Équilibré",
                'description': "Configuration standard, carte apprise après 3 révisions correctes"
            },
            'intensive': {
                'required_reviews_to_learn': 5,
                'auto_mark_learned': True,
                'reset_on_wrong_answer': True,
                'name': "Intensif - Maîtrise complète",
                'description': "Pour une mémorisation solide, avec reset en cas d'erreur"
            },
            'expert': {
                'required_reviews_to_learn': 10,
                'auto_mark_learned': False,
                'reset_on_wrong_answer': True,
                'name': "Expert - Contrôle total",
                'description': "Contrôle manuel de l'apprentissage, parfait pour les experts"
            },
            'custom': {
                'required_reviews_to_learn': self.required_reviews_to_learn,
                'auto_mark_learned': self.auto_mark_learned,
                'reset_on_wrong_answer': self.reset_on_wrong_answer,
                'name': "Personnalisé",
                'description': "Configuration personnalisée"
            }
        }
    
    def apply_learning_preset(self, preset_name):
        """
        Applique un preset de configuration d'apprentissage
        
        Args:
            preset_name (str): Nom du preset à appliquer
        """
        presets = self.get_learning_presets()
        
        if preset_name in presets and preset_name != 'custom':
            preset = presets[preset_name]
            self.required_reviews_to_learn = preset['required_reviews_to_learn']
            self.auto_mark_learned = preset['auto_mark_learned']
            self.reset_on_wrong_answer = preset['reset_on_wrong_answer']
            self.save()
            
            # Recalculer le statut des cartes selon les nouveaux paramètres
            self.recalculate_cards_learned_status()
            
            return True
        return False
    
    def recalculate_cards_learned_status(self):
        """
        Recalcule le statut d'apprentissage de toutes les cartes du deck
        selon les nouveaux paramètres
        """
        for card in self.flashcards.all():
            old_learned_status = card.learned
            
            if self.auto_mark_learned:
                # Marquer comme apprise si le nombre de révisions correctes est atteint
                card.learned = card.correct_reviews_count >= self.required_reviews_to_learn
            else:
                # Si auto_mark_learned est désactivé, ne pas changer le statut automatiquement
                # sauf si la carte était marquée automatiquement avant
                pass
            
            if old_learned_status != card.learned:
                card.save(update_fields=['learned'])
    
    def get_learning_statistics(self):
        """Retourne les statistiques d'apprentissage du deck"""
        cards = self.flashcards.all()
        total_cards = cards.count()
        
        if total_cards == 0:
            return {
                'total_cards': 0,
                'learned_cards': 0,
                'average_progress': 0,
                'completion_rate': 0,
                'cards_needing_review': 0
            }
        
        learned_cards = cards.filter(learned=True).count()
        
        # Calcul de la progression moyenne
        total_progress = sum(
            min(card.correct_reviews_count / self.required_reviews_to_learn, 1.0) 
            for card in cards
        )
        average_progress = (total_progress / total_cards) * 100
        
        # Cartes nécessitant une révision
        cards_needing_review = cards.filter(
            learned=False,
            correct_reviews_count__lt=self.required_reviews_to_learn
        ).count()
        
        return {
            'total_cards': total_cards,
            'learned_cards': learned_cards,
            'average_progress': round(average_progress, 1),
            'completion_rate': round((learned_cards / total_cards) * 100, 1),
            'cards_needing_review': cards_needing_review,
            'required_reviews': self.required_reviews_to_learn,
            'auto_mark_enabled': self.auto_mark_learned,
            'reset_on_wrong': self.reset_on_wrong_answer
        }
        
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
    
    # Champs de langue pour le recto et le verso
    front_language = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Code de langue pour le recto (ex: 'fr', 'en', 'es')"
    )
    back_language = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Code de langue pour le verso (ex: 'fr', 'en', 'es')"
    )
    
    learned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    review_count = models.PositiveIntegerField(default=0)
    next_review = models.DateTimeField(null=True, blank=True)
    
    # Nouveau système de comptage pour les paramètres d'apprentissage
    correct_reviews_count = models.PositiveIntegerField(
        default=0,
        help_text="Nombre de révisions correctes consécutives"
    )
    total_reviews_count = models.PositiveIntegerField(
        default=0,
        help_text="Nombre total de révisions"
    )

    class Meta:
        app_label = 'revision'
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
        self.correct_reviews_count = 0
        self.total_reviews_count = 0
        self.save()
    
    def update_review_progress(self, is_correct=True):
        """
        Met à jour le progrès de révision selon les paramètres du deck
        
        Args:
            is_correct (bool): Si la révision est correcte
        """
        self.total_reviews_count += 1
        self.last_reviewed = timezone.now()
        self.review_count += 1
        
        if is_correct:
            self.correct_reviews_count += 1
            
            # Vérifier si la carte doit être marquée comme apprise
            if (self.deck.auto_mark_learned and 
                self.correct_reviews_count >= self.deck.required_reviews_to_learn):
                self.learned = True
        else:
            # Si mauvaise réponse et reset activé, remettre à zéro
            if self.deck.reset_on_wrong_answer:
                self.correct_reviews_count = 0
                self.learned = False
        
        self.save()
    
    @property
    def learning_progress_percentage(self):
        """Calcule le pourcentage de progression vers l'apprentissage"""
        if self.learned:
            return 100
        
        # Éviter la division par zéro
        if self.deck.required_reviews_to_learn == 0:
            return 100  # Si 0 révision requise, considérer comme 100%
        
        return min(
            (self.correct_reviews_count / self.deck.required_reviews_to_learn) * 100,
            100
        )
    
    @property
    def reviews_remaining_to_learn(self):
        """Nombre de révisions correctes restantes pour marquer comme apprise"""
        if self.learned:
            return 0
        return max(0, self.deck.required_reviews_to_learn - self.correct_reviews_count)