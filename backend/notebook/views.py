# notes/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from .models import Note, NoteCategory, Tag, SharedNote
from .serializers import (
    NoteSerializer, NoteCategorySerializer, TagSerializer,
    SharedNoteSerializer, NoteDetailSerializer
)

class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

class NoteCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = NoteCategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NoteCategory.objects.filter(
            user=self.request.user,
            parent=None  # Retourner uniquement les catégories racines
        )

class NoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'language', 'note_type', 'priority', 'is_pinned', 'is_archived']
    search_fields = ['title', 'content', 'translation', 'tags__name']
    ordering_fields = ['created_at', 'updated_at', 'last_reviewed', 'review_count', 'difficulty']
    ordering = ['-is_pinned', '-updated_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NoteDetailSerializer
        return NoteSerializer

    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user)
        
        # Filtrage par tags multiples
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__name__in=tags).distinct()

        # Filtrage par date de création
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)

        # Filtrage par besoin de révision
        needs_review = self.request.query_params.get('needs_review')
        if needs_review:
            queryset = queryset.filter(needs_review=True)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            context['tags'] = self.request.data.get('tags', [])
        return context

    @action(detail=True, methods=['post'])
    def mark_reviewed(self, request, pk=None):
        """Marquer une note comme révisée."""
        note = self.get_object()
        note.mark_reviewed()
        serializer = self.get_serializer(note)
        return Response(serializer.data)

    @action(detail=False)
    def due_for_review(self, request):
        """Récupérer toutes les notes qui doivent être révisées."""
        notes = self.get_queryset().filter(needs_review=True)
        page = self.paginate_queryset(notes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def by_language(self, request):
        """Récupérer les notes groupées par langue."""
        language = request.query_params.get('language')
        if language:
            notes = self.get_queryset().filter(language=language)
            serializer = self.get_serializer(notes, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def statistics(self, request):
        """Récupérer des statistiques sur les notes."""
        queryset = self.get_queryset()
        return Response({
            'total_notes': queryset.count(),
            'notes_by_type': {
                note_type: queryset.filter(note_type=note_type).count()
                for note_type, _ in Note.TYPE_CHOICES
            },
            'notes_by_language': {
                language: queryset.filter(language=language).count()
                for language, _ in LANGUAGE_CHOICES
            },
            'notes_needing_review': queryset.filter(needs_review=True).count(),
            'notes_by_difficulty': {
                difficulty: queryset.filter(difficulty=difficulty).count()
                for difficulty in range(1, 6)
            }
        })

class SharedNoteViewSet(viewsets.ModelViewSet):
    serializer_class = SharedNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retourner les notes partagées avec l'utilisateur et les notes que l'utilisateur a partagées
        return SharedNote.objects.filter(
            Q(shared_with=self.request.user) | Q(note__user=self.request.user)
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['note_id'] = self.request.data.get('note')
        return context