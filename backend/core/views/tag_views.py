"""
Vues API pour le système de tags global Linguify
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.db import transaction
from django.shortcuts import get_object_or_404
from ..models.tags import Tag, TagRelation, get_tags_for_object, add_tag_to_object, remove_tag_from_object
from ..serializers.tag_serializers import (
    TagSerializer, TagListSerializer, TagRelationSerializer,
    TagCreateSerializer, TagUsageSerializer, ObjectTagsSerializer,
    PopularTagsSerializer, TagSearchSerializer
)


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des tags globaux
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TagListSerializer
        elif self.action == 'create':
            return TagCreateSerializer
        return TagSerializer
    
    def get_queryset(self):
        """Filtre les tags par utilisateur connecté"""
        queryset = Tag.objects.filter(user=self.request.user)
        
        # Filtres optionnels
        active_only = self.request.query_params.get('active_only', 'true').lower() == 'true'
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        favorites_only = self.request.query_params.get('favorites_only', 'false').lower() == 'true'
        if favorites_only:
            queryset = queryset.filter(is_favorite=True)
        
        app_name = self.request.query_params.get('app_name')
        if app_name:
            field_name = f'usage_count_{app_name}'
            if hasattr(Tag, field_name):
                filter_kwargs = {f'{field_name}__gt': 0}
                queryset = queryset.filter(**filter_kwargs)
        
        # Recherche
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('-is_favorite', '-usage_count_total', 'name')
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Récupère les tags populaires et suggestions"""
        user = request.user
        
        # Tags les plus utilisés
        most_used = Tag.objects.filter(user=user, is_active=True).order_by('-usage_count_total')[:10]
        
        # Tags récents
        recent = Tag.objects.filter(user=user, is_active=True).order_by('-created_at')[:5]
        
        # Tags favoris
        favorites = Tag.objects.filter(user=user, is_active=True, is_favorite=True).order_by('name')
        
        # Couleurs suggérées
        suggested_colors = Tag.get_popular_colors()
        
        data = {
            'most_used': TagListSerializer(most_used, many=True).data,
            'recent': TagListSerializer(recent, many=True).data,
            'favorites': TagListSerializer(favorites, many=True).data,
            'suggested_colors': suggested_colors
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Recherche avancée de tags"""
        serializer = TagSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data.get('query', '')
        app_name = serializer.validated_data.get('app_name')
        active_only = serializer.validated_data.get('active_only', True)
        favorites_only = serializer.validated_data.get('favorites_only', False)
        limit = serializer.validated_data.get('limit', 20)
        
        queryset = Tag.objects.filter(user=request.user)
        
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        if favorites_only:
            queryset = queryset.filter(is_favorite=True)
        
        if app_name:
            field_name = f'usage_count_{app_name}'
            if hasattr(Tag, field_name):
                filter_kwargs = {f'{field_name}__gt': 0}
                queryset = queryset.filter(**filter_kwargs)
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        
        queryset = queryset.order_by('-is_favorite', '-usage_count_total', 'name')[:limit]
        
        return Response(TagListSerializer(queryset, many=True).data)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Bascule le statut favori d'un tag"""
        tag = self.get_object()
        tag.is_favorite = not tag.is_favorite
        tag.save(update_fields=['is_favorite'])
        return Response(TagSerializer(tag).data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Bascule le statut actif d'un tag"""
        tag = self.get_object()
        tag.is_active = not tag.is_active
        tag.save(update_fields=['is_active'])
        return Response(TagSerializer(tag).data)
    
    @action(detail=True, methods=['get'])
    def usage_stats(self, request, pk=None):
        """Statistiques détaillées d'usage d'un tag"""
        tag = self.get_object()
        
        # Récupérer les relations pour ce tag
        relations = TagRelation.objects.filter(tag=tag).select_related('created_by')
        
        # Statistiques par app
        stats_by_app = {}
        for app in ['notebook', 'todo', 'calendar', 'revision', 'documents', 'community']:
            app_relations = relations.filter(app_name=app)
            stats_by_app[app] = {
                'count': app_relations.count(),
                'models': list(app_relations.values('model_name').distinct().values_list('model_name', flat=True))
            }
        
        # Dernière utilisation
        last_relation = relations.order_by('-created_at').first()
        last_used = last_relation.created_at if last_relation else None
        
        data = {
            'tag_id': tag.id,
            'tag_name': tag.name,
            'tag_color': tag.color,
            'total_usage': tag.usage_count_total,
            'usage_by_app': tag.get_usage_by_app(),
            'detailed_stats': stats_by_app,
            'primary_app': tag.get_primary_app(),
            'last_used': last_used,
            'created_at': tag.created_at
        }
        
        return Response(data)


class TagRelationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des relations tag-objet
    """
    
    serializer_class = TagRelationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les relations par tags de l'utilisateur"""
        return TagRelation.objects.filter(
            tag__user=self.request.user
        ).select_related('tag', 'created_by')


class ObjectTagsViewSet(viewsets.GenericViewSet):
    """
    ViewSet pour gérer les tags d'objets spécifiques
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def get_object_tags(self, request):
        """Récupère tous les tags associés à un objet"""
        app_name = request.query_params.get('app_name')
        model_name = request.query_params.get('model_name') 
        object_id = request.query_params.get('object_id')
        
        if not all([app_name, model_name, object_id]):
            return Response(
                {'error': 'app_name, model_name et object_id sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tags = get_tags_for_object(app_name, model_name, object_id, request.user)
            return Response(TagListSerializer(tags, many=True).data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def set_object_tags(self, request):
        """Définit les tags d'un objet (remplace tous les tags existants)"""
        serializer = ObjectTagsSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        app_name = serializer.validated_data['app_name']
        model_name = serializer.validated_data['model_name']
        object_id = serializer.validated_data['object_id']
        tag_ids = serializer.validated_data['tag_ids']
        
        try:
            with transaction.atomic():
                # Supprimer toutes les relations existantes
                TagRelation.objects.filter(
                    app_name=app_name,
                    model_name=model_name,
                    object_id=object_id,
                    tag__user=request.user
                ).delete()
                
                # Ajouter les nouvelles relations
                for tag_id in tag_ids:
                    tag = get_object_or_404(Tag, id=tag_id, user=request.user)
                    add_tag_to_object(tag, app_name, model_name, object_id, request.user)
                
                # Récupérer et retourner les tags mis à jour
                tags = get_tags_for_object(app_name, model_name, object_id, request.user)
                return Response(TagListSerializer(tags, many=True).data)
                
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def add_tag_to_object(self, request):
        """Ajoute un tag à un objet"""
        tag_id = request.data.get('tag_id')
        app_name = request.data.get('app_name')
        model_name = request.data.get('model_name')
        object_id = request.data.get('object_id')
        
        if not all([tag_id, app_name, model_name, object_id]):
            return Response(
                {'error': 'tag_id, app_name, model_name et object_id sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tag = get_object_or_404(Tag, id=tag_id, user=request.user)
            relation = add_tag_to_object(tag, app_name, model_name, object_id, request.user)
            return Response(TagRelationSerializer(relation).data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['delete'])
    def remove_tag_from_object(self, request):
        """Retire un tag d'un objet"""
        tag_id = request.data.get('tag_id')
        app_name = request.data.get('app_name')
        model_name = request.data.get('model_name')
        object_id = request.data.get('object_id')
        
        if not all([tag_id, app_name, model_name, object_id]):
            return Response(
                {'error': 'tag_id, app_name, model_name et object_id sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tag = get_object_or_404(Tag, id=tag_id, user=request.user)
            removed = remove_tag_from_object(tag, app_name, model_name, object_id)
            
            return Response({
                'success': removed,
                'message': 'Tag retiré avec succès' if removed else 'Tag non trouvé sur cet objet'
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )