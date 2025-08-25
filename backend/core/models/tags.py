"""
Système de tags global et cross-apps pour Linguify
Vision: Un système unifié permettant de gérer des tags à travers toutes les applications
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone
import uuid

User = get_user_model()


class Tag(models.Model):
    """
    Tags globaux cross-apps - Système unifié Linguify
    
    Ces tags peuvent être utilisés dans:
    - Notebook (notes)
    - Todo (tâches et projets) 
    - Calendar (événements)
    - Revision (decks de cartes)
    - Documents (fichiers et dossiers)
    - Community (posts et discussions)
    """
    
    # Identifiants
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='linguify_tags')
    
    # Propriétés du tag
    name = models.CharField(
        max_length=50, 
        validators=[MinLengthValidator(1), MaxLengthValidator(50)],
        help_text="Nom du tag (1-50 caractères)"
    )
    color = models.CharField(
        max_length=7, 
        default='#3B82F6',
        help_text="Couleur hexadécimale du tag"
    )
    
    # Description optionnelle
    description = models.TextField(
        blank=True, 
        max_length=200,
        help_text="Description optionnelle du tag (max 200 caractères)"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Compteurs d'usage cross-apps
    usage_count_total = models.PositiveIntegerField(default=0)
    usage_count_notebook = models.PositiveIntegerField(default=0)
    usage_count_todo = models.PositiveIntegerField(default=0)
    usage_count_calendar = models.PositiveIntegerField(default=0)
    usage_count_revision = models.PositiveIntegerField(default=0)
    usage_count_documents = models.PositiveIntegerField(default=0)
    usage_count_community = models.PositiveIntegerField(default=0)
    
    # Paramètres
    is_active = models.BooleanField(default=True)
    is_favorite = models.BooleanField(
        default=False,
        help_text="Tags favoris affichés en premier"
    )
    
    class Meta:
        verbose_name = 'Tag Global'
        verbose_name_plural = 'Tags Globaux'
        unique_together = ['user', 'name']
        ordering = ['-is_favorite', '-usage_count_total', 'name']
        indexes = [
            models.Index(fields=['user', 'name']),
            models.Index(fields=['user', '-usage_count_total']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"#{self.name}"
    
    @property
    def hex_to_rgb(self):
        """Convertit la couleur hex en RGB pour les styles avec transparence"""
        hex_color = self.color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16) 
            b = int(hex_color[4:6], 16)
            return f"{r}, {g}, {b}"
        return "59, 130, 246"  # Fallback bleu Linguify
    
    def increment_usage(self, app_name=None):
        """
        Incrémente le compteur d'usage pour une app spécifique
        
        Args:
            app_name (str): notebook, todo, calendar, revision, documents, community
        """
        self.usage_count_total += 1
        
        if app_name:
            field_name = f'usage_count_{app_name}'
            if hasattr(self, field_name):
                current_value = getattr(self, field_name)
                setattr(self, field_name, current_value + 1)
        
        self.save(update_fields=[
            'usage_count_total', 
            f'usage_count_{app_name}' if app_name else None
        ])
    
    def decrement_usage(self, app_name=None):
        """
        Décrémente le compteur d'usage pour une app spécifique
        
        Args:
            app_name (str): notebook, todo, calendar, revision, documents, community
        """
        if self.usage_count_total > 0:
            self.usage_count_total -= 1
        
        if app_name:
            field_name = f'usage_count_{app_name}'
            if hasattr(self, field_name):
                current_value = getattr(self, field_name)
                if current_value > 0:
                    setattr(self, field_name, current_value - 1)
        
        self.save(update_fields=[
            'usage_count_total', 
            f'usage_count_{app_name}' if app_name else None
        ])
    
    def get_usage_by_app(self):
        """Retourne un dictionnaire de l'usage par app"""
        return {
            'notebook': self.usage_count_notebook,
            'todo': self.usage_count_todo,
            'calendar': self.usage_count_calendar,
            'revision': self.usage_count_revision,
            'documents': self.usage_count_documents,
            'community': self.usage_count_community,
        }
    
    def get_primary_app(self):
        """Retourne l'app où le tag est le plus utilisé"""
        usage_by_app = self.get_usage_by_app()
        if not any(usage_by_app.values()):
            return None
        return max(usage_by_app.items(), key=lambda x: x[1])[0]
    
    def recalculate_usage_counts(self):
        """
        Recalcule les compteurs d'usage basés sur les TagRelations existantes
        """
        # Reset all counters
        self.usage_count_total = 0
        self.usage_count_notebook = 0
        self.usage_count_todo = 0
        self.usage_count_calendar = 0
        self.usage_count_revision = 0
        self.usage_count_documents = 0
        self.usage_count_community = 0
        
        # Count relations by app
        relations = self.relations.all()
        for relation in relations:
            app_name = relation.app_name
            field_name = f'usage_count_{app_name}'
            if hasattr(self, field_name):
                current_value = getattr(self, field_name)
                setattr(self, field_name, current_value + 1)
            self.usage_count_total += 1
        
        # Save all updated fields
        self.save(update_fields=[
            'usage_count_total', 'usage_count_notebook', 'usage_count_todo',
            'usage_count_calendar', 'usage_count_revision', 'usage_count_documents',
            'usage_count_community'
        ])
    
    @classmethod
    def get_user_tags(cls, user, app_name=None, active_only=True):
        """
        Récupère les tags d'un utilisateur
        
        Args:
            user: L'utilisateur
            app_name (str, optional): Filtrer par app
            active_only (bool): Seulement les tags actifs
            
        Returns:
            QuerySet: Tags filtrés
        """
        queryset = cls.objects.filter(user=user)
        
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        if app_name:
            # Filtrer les tags qui ont été utilisés dans cette app
            field_name = f'usage_count_{app_name}'
            if hasattr(cls, field_name):
                filter_kwargs = {f'{field_name}__gt': 0}
                queryset = queryset.filter(**filter_kwargs)
        
        return queryset
    
    @classmethod
    def create_default_tags(cls, user):
        """
        Crée des tags par défaut pour un nouvel utilisateur
        
        Args:
            user: L'utilisateur pour qui créer les tags
            
        Returns:
            list: Liste des tags créés
        """
        default_tags = [
            {'name': 'Important', 'color': '#EF4444', 'description': 'Éléments importants à ne pas oublier'},
            {'name': 'Personnel', 'color': '#10B981', 'description': 'Contenus personnels'},
            {'name': 'Travail', 'color': '#3B82F6', 'description': 'Contenus liés au travail'},
            {'name': 'Études', 'color': '#8B5CF6', 'description': 'Contenus académiques et éducatifs'},
            {'name': 'Urgent', 'color': '#F59E0B', 'description': 'Éléments urgents à traiter'},
        ]
        
        created_tags = []
        for tag_data in default_tags:
            tag, created = cls.objects.get_or_create(
                user=user,
                name=tag_data['name'],
                defaults={
                    'color': tag_data['color'],
                    'description': tag_data['description'],
                    'is_favorite': tag_data['name'] in ['Important', 'Urgent']
                }
            )
            if created:
                created_tags.append(tag)
        
        return created_tags
    
    @classmethod
    def get_popular_colors(cls):
        """Retourne les couleurs les plus populaires pour les nouveaux tags"""
        return [
            '#3B82F6',  # Bleu Linguify
            '#EF4444',  # Rouge
            '#10B981',  # Vert
            '#F59E0B',  # Orange
            '#8B5CF6',  # Violet
            '#06B6D4',  # Cyan
            '#EC4899',  # Rose
            '#6B7280',  # Gris
        ]


class TagRelation(models.Model):
    """
    Relation générique pour lier des tags à n'importe quel modèle de n'importe quelle app
    
    Cette table permet d'associer des tags globaux à:
    - Notes (Notebook)
    - Tâches et Projets (Todo)  
    - Événements (Calendar)
    - Decks de cartes (Revision)
    - Documents et dossiers (Documents)
    - Posts et discussions (Community)
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='relations')
    
    # Identification de l'objet taggé (Generic Foreign Key pattern)
    app_name = models.CharField(
        max_length=50,
        help_text="Nom de l'app (notebook, todo, calendar, etc.)"
    )
    model_name = models.CharField(
        max_length=50,
        help_text="Nom du modèle (Note, Task, Event, etc.)"
    )
    object_id = models.UUIDField(help_text="ID de l'objet taggé")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Relation Tag'
        verbose_name_plural = 'Relations Tags'
        unique_together = ['tag', 'app_name', 'model_name', 'object_id']
        indexes = [
            models.Index(fields=['app_name', 'model_name', 'object_id']),
            models.Index(fields=['tag', 'app_name']),
            models.Index(fields=['created_by', 'app_name']),
        ]
    
    def __str__(self):
        return f"{self.tag.name} -> {self.app_name}.{self.model_name}({self.object_id})"
    
    def save(self, *args, **kwargs):
        """Override save pour mettre à jour les compteurs d'usage"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Incrémenter le compteur d'usage du tag pour cette app
            self.tag.increment_usage(self.app_name)
    
    def delete(self, *args, **kwargs):
        """Override delete pour mettre à jour les compteurs d'usage"""
        app_name = self.app_name
        tag = self.tag
        super().delete(*args, **kwargs)
        
        # Décrémenter le compteur d'usage
        tag.decrement_usage(app_name)


# Helper functions pour faciliter l'usage dans les autres apps

def get_tags_for_object(app_name, model_name, object_id, user=None):
    """
    Récupère tous les tags associés à un objet
    
    Args:
        app_name (str): Nom de l'app
        model_name (str): Nom du modèle  
        object_id (UUID): ID de l'objet
        user (User, optional): Filtrer par utilisateur
        
    Returns:
        QuerySet: Tags associés à l'objet
    """
    relations = TagRelation.objects.filter(
        app_name=app_name,
        model_name=model_name,
        object_id=object_id
    )
    
    if user:
        relations = relations.filter(tag__user=user)
    
    return Tag.objects.filter(
        id__in=relations.values_list('tag_id', flat=True)
    )


def add_tag_to_object(tag, app_name, model_name, object_id, user):
    """
    Ajoute un tag à un objet
    
    Args:
        tag (Tag): Le tag à ajouter
        app_name (str): Nom de l'app
        model_name (str): Nom du modèle
        object_id (UUID): ID de l'objet
        user (User): Utilisateur qui effectue l'action
        
    Returns:
        TagRelation: La relation créée (ou existante)
    """
    relation, created = TagRelation.objects.get_or_create(
        tag=tag,
        app_name=app_name,
        model_name=model_name,
        object_id=object_id,
        defaults={'created_by': user}
    )
    return relation


def remove_tag_from_object(tag, app_name, model_name, object_id):
    """
    Retire un tag d'un objet
    
    Args:
        tag (Tag): Le tag à retirer
        app_name (str): Nom de l'app
        model_name (str): Nom du modèle
        object_id (UUID): ID de l'objet
        
    Returns:
        bool: True si le tag a été retiré, False s'il n'existait pas
    """
    try:
        relation = TagRelation.objects.get(
            tag=tag,
            app_name=app_name,
            model_name=model_name,
            object_id=object_id
        )
        relation.delete()
        return True
    except TagRelation.DoesNotExist:
        return False


def get_objects_with_tag(tag, app_name=None, model_name=None):
    """
    Récupère tous les objets qui ont un tag donné
    
    Args:
        tag (Tag): Le tag à rechercher
        app_name (str, optional): Filtrer par app
        model_name (str, optional): Filtrer par modèle
        
    Returns:
        QuerySet: Relations qui correspondent aux critères
    """
    relations = TagRelation.objects.filter(tag=tag)
    
    if app_name:
        relations = relations.filter(app_name=app_name)
    
    if model_name:
        relations = relations.filter(model_name=model_name)
    
    return relations