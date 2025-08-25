"""
Serializers pour le système de tags global Linguify
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models.tags import Tag, TagRelation

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer pour les tags globaux
    """
    
    # Champs calculés
    hex_to_rgb = serializers.ReadOnlyField()
    primary_app = serializers.ReadOnlyField(source='get_primary_app')
    usage_by_app = serializers.ReadOnlyField(source='get_usage_by_app')
    
    # Champs personnalisés pour l'affichage
    display_name = serializers.SerializerMethodField()
    badge_style = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'display_name',
            'color',
            'hex_to_rgb',
            'description',
            'is_active',
            'is_favorite',
            'usage_count_total',
            'usage_count_notebook',
            'usage_count_todo',
            'usage_count_calendar',
            'usage_count_revision',
            'usage_count_documents',
            'usage_count_community',
            'primary_app',
            'usage_by_app',
            'badge_style',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'usage_count_total',
            'usage_count_notebook',
            'usage_count_todo',
            'usage_count_calendar',
            'usage_count_revision', 
            'usage_count_documents',
            'usage_count_community',
            'created_at',
            'updated_at'
        ]
    
    def get_display_name(self, obj):
        """Nom d'affichage avec symbole #"""
        return f"#{obj.name}"
    
    def get_badge_style(self, obj):
        """Style CSS pour l'affichage du badge"""
        return {
            'backgroundColor': obj.color,
            'color': 'white',
            'borderRadius': '12px',
            'padding': '4px 8px',
            'fontSize': '0.8rem',
            'fontWeight': '500'
        }
    
    def validate_name(self, value):
        """Validation du nom du tag"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom du tag ne peut pas être vide.")
        
        value = value.strip()
        
        if len(value) < 1:
            raise serializers.ValidationError("Le nom doit contenir au moins 1 caractère.")
        
        if len(value) > 50:
            raise serializers.ValidationError("Le nom ne peut pas dépasser 50 caractères.")
        
        # Vérifier l'unicité pour l'utilisateur
        user = self.context['request'].user if 'request' in self.context else None
        if user:
            existing = Tag.objects.filter(user=user, name__iexact=value)
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
            if existing.exists():
                raise serializers.ValidationError("Vous avez déjà un tag avec ce nom.")
        
        return value
    
    def validate_color(self, value):
        """Validation de la couleur hexadécimale"""
        if not value.startswith('#'):
            raise serializers.ValidationError("La couleur doit commencer par #.")
        
        if len(value) != 7:
            raise serializers.ValidationError("La couleur doit être au format #RRGGBB.")
        
        try:
            int(value[1:], 16)
        except ValueError:
            raise serializers.ValidationError("Format de couleur invalide.")
        
        return value
    
    def create(self, validated_data):
        """Création d'un nouveau tag"""
        # Ajouter l'utilisateur automatiquement
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class TagListSerializer(TagSerializer):
    """
    Serializer simplifié pour les listes de tags
    """
    
    class Meta(TagSerializer.Meta):
        fields = [
            'id',
            'name',
            'display_name', 
            'color',
            'usage_count_total',
            'is_favorite',
            'badge_style'
        ]


class TagRelationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les relations tag-objet
    """
    
    tag = TagListSerializer(read_only=True)
    tag_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = TagRelation
        fields = [
            'id',
            'tag',
            'tag_id', 
            'app_name',
            'model_name',
            'object_id',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_tag_id(self, value):
        """Validation de l'existence du tag"""
        user = self.context['request'].user
        try:
            tag = Tag.objects.get(id=value, user=user, is_active=True)
        except Tag.DoesNotExist:
            raise serializers.ValidationError("Tag introuvable ou inactif.")
        return value
    
    def create(self, validated_data):
        """Création d'une nouvelle relation tag-objet"""
        user = self.context['request'].user
        validated_data['created_by'] = user
        return super().create(validated_data)


class TagCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création rapide de tags
    """
    
    class Meta:
        model = Tag
        fields = ['name', 'color', 'description']
    
    def validate_name(self, value):
        """Validation simplifiée du nom"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom est requis.")
        
        value = value.strip()
        if len(value) > 50:
            raise serializers.ValidationError("Maximum 50 caractères.")
        
        # Vérifier unicité pour l'utilisateur
        user = self.context['request'].user
        if Tag.objects.filter(user=user, name__iexact=value).exists():
            raise serializers.ValidationError("Vous avez déjà un tag avec ce nom.")
        
        return value
    
    def create(self, validated_data):
        """Création avec utilisateur automatique"""
        user = self.context['request'].user
        validated_data['user'] = user
        
        # Valeurs par défaut
        if 'color' not in validated_data:
            validated_data['color'] = '#3B82F6'  # Bleu Linguify par défaut
        
        return super().create(validated_data)


class TagUsageSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques d'usage des tags
    """
    
    tag_id = serializers.UUIDField()
    tag_name = serializers.CharField()
    tag_color = serializers.CharField()
    total_usage = serializers.IntegerField()
    usage_by_app = serializers.DictField()
    primary_app = serializers.CharField(allow_null=True)
    last_used = serializers.DateTimeField(allow_null=True)


class ObjectTagsSerializer(serializers.Serializer):
    """
    Serializer pour gérer les tags d'un objet spécifique
    """
    
    app_name = serializers.CharField(max_length=50)
    model_name = serializers.CharField(max_length=50)
    object_id = serializers.UUIDField()
    tag_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=True
    )
    
    def validate_tag_ids(self, value):
        """Validation des IDs de tags"""
        user = self.context['request'].user
        
        # Vérifier que tous les tags existent et appartiennent à l'utilisateur
        existing_tags = Tag.objects.filter(
            id__in=value,
            user=user,
            is_active=True
        ).values_list('id', flat=True)
        
        missing_tags = set(value) - set(existing_tags)
        if missing_tags:
            raise serializers.ValidationError(
                f"Tags introuvables: {', '.join(map(str, missing_tags))}"
            )
        
        return value


class PopularTagsSerializer(serializers.Serializer):
    """
    Serializer pour les tags populaires et suggestions
    """
    
    most_used = TagListSerializer(many=True)
    recent = TagListSerializer(many=True)
    favorites = TagListSerializer(many=True)
    suggested_colors = serializers.ListField(child=serializers.CharField())


class TagSearchSerializer(serializers.Serializer):
    """
    Serializer pour la recherche de tags
    """
    
    query = serializers.CharField(max_length=100, required=False, allow_blank=True)
    app_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    active_only = serializers.BooleanField(default=True)
    favorites_only = serializers.BooleanField(default=False)
    limit = serializers.IntegerField(min_value=1, max_value=100, default=20)