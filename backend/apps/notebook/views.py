# -*- coding: utf-8 -*-
# Part of Open Linguify. See LICENSE file for full copyright and licensing details.
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.pagination import CursorPagination, PageNumberPagination
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
import base64

from .models import Note, NoteCategory, Tag, SharedNote
from .serializers import (
    NoteSerializer, NoteCategorySerializer, TagSerializer,
    SharedNoteSerializer, NoteDetailSerializer, NoteListSerializer
)


class EnhancedCursorPagination(CursorPagination):
    """
    Pagination à curseur optimisée pour de larges jeux de données.
    Utilise un curseur encodé en base64 qui représente une position dans le jeu de données.
    Plus performant que la pagination par offset pour les grandes collections.
    """
    page_size = 50  # Nombre d'éléments par page
    page_size_query_param = 'page_size'  # Permettre aux clients de définir la taille de la page
    max_page_size = 200  # Taille maximale de page pour éviter surcharge de serveur
    ordering = '-updated_at'  # Champ à utiliser pour l'ordre des données (clé de curseur)
    cursor_query_param = 'cursor'  # Nom du paramètre de requête pour le curseur

    def encode_cursor(self, cursor):
        """Encodage personnalisé du curseur pour le rendre plus compact"""
        tokens = {}
        if cursor.offset != 0:
            tokens['o'] = str(cursor.offset)
        if cursor.reverse:
            tokens['r'] = '1'
        if cursor.position:
            tokens['p'] = cursor.position
        
        querystring = '&'.join(f'{k}={v}' for k, v in tokens.items())
        return base64.b64encode(querystring.encode('utf-8')).decode('utf-8')

    def decode_cursor(self, request):
        """Décodage personnalisé du curseur"""
        from rest_framework.pagination import Cursor
        
        encoded = request.query_params.get(self.cursor_query_param)
        if encoded is None:
            return None
        
        try:
            # Assurons-nous que encoded est une chaîne de caractères avant d'appeler encode
            if isinstance(encoded, str):
                querystring = base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
            else:
                querystring = base64.b64decode(encoded).decode('utf-8')
                
            tokens = {}
            for pair in querystring.split('&'):
                if not pair:
                    continue
                key, value = pair.split('=', 1)
                tokens[key] = value
            
            offset = int(tokens.get('o', '0'))
            reverse = 'r' in tokens
            position = tokens.get('p', None)
            
            return Cursor(offset=offset, reverse=reverse, position=position)
        except (ValueError, KeyError, TypeError, AttributeError):
            return None


class StandardResultsSetPagination(PageNumberPagination):
    """
    Pagination standard par numéro de page, 
    utilisée pour les endpoints moins critiques en performance
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user).annotate(
            notes_count=Count('note')
        )

    @action(detail=True, methods=['post'])
    def merge(self, request, pk=None):
        """Fusionner ce tag avec un autre"""
        target_tag_id = request.data.get('target_tag_id')
        if not target_tag_id:
            raise ValidationError({"target_tag_id": "This field is required."})

        source_tag = self.get_object()
        try:
            target_tag = Tag.objects.get(
                id=target_tag_id,
                user=request.user
            )
        except Tag.DoesNotExist:
            raise ValidationError({"target_tag_id": "Invalid tag ID."})

        with transaction.atomic():
            # Déplacer toutes les notes du tag source vers le tag cible
            source_tag.note_set.update(tags=target_tag)
            source_tag.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class NoteCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = NoteCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = NoteCategory.objects.filter(user=self.request.user)
        if self.action == 'list':
            # Pour la liste principale, ne retourner que les catégories racines
            queryset = queryset.filter(parent=None)
        return queryset.prefetch_related(
            Prefetch(
                'note_set',
                queryset=Note.objects.order_by('-created_at').all()[:5],
                to_attr='recent_notes'
            )
        )

    @action(detail=True)
    def tree(self, request, pk=None):
        """Retourner l'arborescence complète à partir de cette catégorie"""
        category = self.get_object()
        serializer = self.get_serializer(category)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """Déplacer une catégorie vers un nouveau parent"""
        new_parent_id = request.data.get('parent_id')
        category = self.get_object()

        if new_parent_id:
            try:
                new_parent = NoteCategory.objects.get(
                    id=new_parent_id,
                    user=request.user
                )
                if new_parent == category or new_parent.parent == category:
                    raise ValidationError(
                        {"parent_id": "Invalid parent category."}
                    )
                category.parent = new_parent
            except NoteCategory.DoesNotExist:
                raise ValidationError({"parent_id": "Invalid parent ID."})
        else:
            category.parent = None
        
        category.save()
        serializer = self.get_serializer(category)
        return Response(serializer.data)

class NoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    pagination_class = StandardResultsSetPagination  # Revenir à la pagination standard pour s'assurer de la stabilité
    filterset_fields = {
        'category': ['exact', 'isnull'],
        'note_type': ['exact', 'in'],
        'priority': ['exact', 'in'],
        'is_pinned': ['exact'],
        'is_archived': ['exact'],
        'created_at': ['gte', 'lte'],
        'updated_at': ['gte', 'lte'],
    }
    search_fields = [
        'title', 'content', 'tags__name',
        'category__name'
    ]
    ordering_fields = [
        'created_at', 'updated_at', 'last_reviewed_at',
        'review_count', 'priority'
    ]
    ordering = ['-is_pinned', '-updated_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return NoteListSerializer
        if self.action == 'retrieve':
            return NoteDetailSerializer
        return NoteSerializer

    def get_queryset(self):
        # Base queryset with optimized joins
        queryset = Note.objects.select_related('category').prefetch_related(
            'tags',
            'sharednote_set__shared_with'
        )

        # Filter by ownership or shared access with query optimization
        # Using subqueries to avoid duplicates in results and reduce joins
        user_id = self.request.user.id
        
        # Special case for retrieve action (getting a single note)
        if self.action == 'retrieve' and 'pk' in self.kwargs:
            # When retrieving a specific note by pk, use a simpler approach
            # that doesn't rely on union() which has limitations with .get()
            note_id = self.kwargs['pk']
            # A user can access a note if they own it or if it's shared with them
            return queryset.filter(
                Q(id=note_id) & (
                    Q(user_id=user_id) | 
                    Q(id__in=SharedNote.objects.filter(
                        shared_with_id=user_id
                    ).values_list('note_id', flat=True))
                )
            )
            
        # Normal case for list and other actions
        user_notes = queryset.filter(user_id=user_id)
        
        # Only add shared notes for list action
        if self.action == 'list':
            shared_notes_ids = SharedNote.objects.filter(
                shared_with_id=user_id
            ).values_list('note_id', flat=True)
            shared_notes = queryset.filter(id__in=shared_notes_ids)
            queryset = user_notes.union(shared_notes)
        else:
            queryset = user_notes

        # Apply additional filters from query params
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__name__in=tags)

        needs_review = self.request.query_params.get('needs_review')
        if needs_review:
            # On ne peut pas filtrer directement sur needs_review car c'est une propriété
            # On doit filtrer sur last_reviewed_at et review_count
            from django.utils import timezone
            from datetime import timedelta
            
            # Filtrer les notes qui n'ont jamais été révisées
            never_reviewed = queryset.filter(last_reviewed_at__isnull=True)
            
            # Pour les notes qui ont été révisées, calculer les dates de prochaine révision
            # basées sur leur nombre de révisions
            review_levels = {
                0: timedelta(days=1),
                1: timedelta(days=3),
                2: timedelta(days=7),
                3: timedelta(days=14),
                4: timedelta(days=30),
                5: timedelta(days=60)
            }
            
            # Construire un filtre complexe pour chaque niveau de révision
            now = timezone.now()
            due_reviews_filter = Q()
            
            for review_count, interval in review_levels.items():
                if review_count < 5:
                    # Notes avec ce nombre exact de révisions
                    due_reviews_filter |= Q(
                        review_count=review_count,
                        last_reviewed_at__lte=now - interval
                    )
                else:
                    # Notes avec 5 révisions ou plus
                    due_reviews_filter |= Q(
                        review_count__gte=review_count,
                        last_reviewed_at__lte=now - interval
                    )
            
            # Combiner avec les notes jamais révisées
            queryset = never_reviewed.union(queryset.filter(due_reviews_filter))

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            # Ensure tags is always a list, never None
            tags = self.request.data.get('tags')
            context['tags'] = tags if tags is not None else []
        return context

    @action(detail=True, methods=['post'])
    def mark_reviewed(self, request, pk=None):
        """Marquer une note comme révisée."""
        note = self.get_object()
        success = request.data.get('success', True)
        
        with transaction.atomic():
            if success:
                note.mark_reviewed()
            note.review_count += 1
            note.save()

        serializer = self.get_serializer(note)
        return Response(serializer.data)

    @action(detail=False)
    def due_for_review(self, request):
        """Récupérer toutes les notes qui doivent être révisées."""
        cache_key = f'notes_due_review_{request.user.id}'
        cached_data = cache.get(cache_key)

        if cached_data is None:
            # On ne peut pas filtrer directement sur needs_review car c'est une propriété
            # Plutôt, nous allons récupérer toutes les notes et filtrer manuellement
            # Mais avec une optimisation pour réduire le nombre d'objets à traiter
            queryset = self.get_queryset()
            # Prétraitement pour réduire le nombre d'éléments à itérer
            from django.utils import timezone
            from datetime import timedelta
            
            # Filtrer d'abord sur les notes jamais révisées ou révisées il y a longtemps
            notes_candidates = list(queryset.filter(
                # Soit jamais révisé
                models.Q(last_reviewed_at__isnull=True) |
                # Soit révisé il y a au moins 1 jour (le délai minimum)
                models.Q(last_reviewed_at__lte=timezone.now() - timedelta(days=1))
            ))
            
            # Ensuite filtrer plus précisément avec la propriété needs_review
            notes = [note for note in notes_candidates if note.needs_review]
            serializer = self.get_serializer(notes, many=True)
            cached_data = serializer.data
            cache.set(cache_key, cached_data, 300)  # Cache for 5 minutes

        return Response(cached_data)

    @action(detail=False)
    def statistics(self, request):
        """Récupérer des statistiques détaillées sur les notes."""
        queryset = self.get_queryset()
        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        
        # Optimisation majeure: faire une seule requête pour obtenir les agrégats
        # au lieu de multiples requêtes individuelles
        from django.db.models import Count, Case, When, IntegerField, Value
        
        # Récupérer les statistiques par type et priorité en une seule requête
        type_priority_stats = queryset.aggregate(
            total_notes=Count('id'),
            reviewed_today=Count(Case(When(last_reviewed_at__date=today, then=Value(1)), output_field=IntegerField())),
            reviewed_this_week=Count(Case(When(last_reviewed_at__gte=week_ago, then=Value(1)), output_field=IntegerField())),
            created_today=Count(Case(When(created_at__date=today, then=Value(1)), output_field=IntegerField())),
            created_this_week=Count(Case(When(created_at__gte=week_ago, then=Value(1)), output_field=IntegerField())),
        )
        
        # Pour le comptage des notes à réviser, on doit les filtrer manuellement
        # Mais avec une optimisation pour réduire le nombre d'objets à traiter
        from django.utils import timezone
        from datetime import timedelta
        
        # Filtrer d'abord sur les notes jamais révisées ou révisées il y a longtemps
        notes_candidates = list(queryset.filter(
            # Soit jamais révisé
            Q(last_reviewed_at__isnull=True) |
            # Soit révisé il y a au moins 1 jour (le délai minimum)
            Q(last_reviewed_at__lte=timezone.now() - timedelta(days=1))
        ))
        
        # Ensuite filtrer plus précisément avec la propriété needs_review
        due_now_count = len([note for note in notes_candidates if note.needs_review])
        
        # Regrouper les notes par type en une seule requête
        type_counts = queryset.values('note_type').annotate(count=Count('id'))
        notes_by_type = {note_type_dict['note_type']: note_type_dict['count'] for note_type_dict in type_counts}
        
        # Convertir les codes de type en libellés lisibles
        type_labels = dict(Note.TYPE_CHOICES)
        notes_by_type_labeled = {type_labels.get(k, k): v for k, v in notes_by_type.items()}
        
        # Regrouper les notes par priorité en une seule requête
        priority_counts = queryset.values('priority').annotate(count=Count('id'))
        notes_by_priority = {priority_dict['priority']: priority_dict['count'] for priority_dict in priority_counts}
        
        # Convertir les codes de priorité en libellés lisibles
        priority_labels = dict(Note.PRIORITY_CHOICES)
        notes_by_priority_labeled = {priority_labels.get(k, k): v for k, v in notes_by_priority.items()}
        
        # Récupérer les statistiques par tag en une seule requête
        tag_stats = Tag.objects.filter(
            user=request.user
        ).annotate(
            notes_count=Count('note')
        ).values('name', 'notes_count')
        
        stats = {
            'total_notes': type_priority_stats['total_notes'],
            'notes_by_type': notes_by_type_labeled,
            'notes_by_priority': notes_by_priority_labeled,
            'review_stats': {
                'due_now': due_now_count,
                'reviewed_today': type_priority_stats['reviewed_today'],
                'reviewed_this_week': type_priority_stats['reviewed_this_week'],
            },
            'creation_stats': {
                'created_today': type_priority_stats['created_today'],
                'created_this_week': type_priority_stats['created_this_week'],
            },
            'tag_stats': tag_stats,
        }

        return Response(stats)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Partager une note avec d'autres utilisateurs."""
        note = self.get_object()
        serializer = SharedNoteSerializer(
            data=request.data,
            context={'request': request, 'note_id': note.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Créer une copie de la note."""
        original_note = self.get_object()
        new_note = Note.objects.create(
            user=request.user,
            title=f"Copy of {original_note.title}",
            content=original_note.content,
            category=original_note.category,
            note_type=original_note.note_type,
            priority=original_note.priority
        )
        new_note.tags.set(original_note.tags.all())
        
        serializer = self.get_serializer(new_note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class SharedNoteViewSet(viewsets.ModelViewSet):
    serializer_class = SharedNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SharedNote.objects.select_related(
            'note', 'note__category', 'shared_with'
        ).filter(
            Q(shared_with=self.request.user) |
            Q(note__user=self.request.user)
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['note_id'] = self.request.data.get('note')
        return context

    def perform_destroy(self, instance):
        if instance.note.user != self.request.user:
            raise PermissionDenied(
                "Only the note owner can remove sharing."
            )
        instance.delete()

    @action(detail=False)
    def shared_with_me(self, request):
        """Récupérer toutes les notes partagées avec l'utilisateur."""
        shared_notes = self.get_queryset().filter(
            shared_with=request.user
        )
        serializer = self.get_serializer(shared_notes, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def shared_by_me(self, request):
        """Récupérer toutes les notes que l'utilisateur a partagées."""
        shared_notes = self.get_queryset().filter(
            note__user=request.user
        )
        serializer = self.get_serializer(shared_notes, many=True)
        return Response(serializer.data)