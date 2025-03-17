# backend/revision/serializers/flashcard_serializers.py
from rest_framework import serializers
from ..models import FlashcardDeck, Flashcard

class FlashcardSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle Flashcard."""
    
    # Ajout d'un champ calculé pour le temps écoulé depuis la dernière révision
    days_since_last_review = serializers.SerializerMethodField()
    # Ajout d'un champ calculé pour savoir si la carte est due pour révision
    is_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Flashcard
        fields = [
            'id', 'deck', 'front_text', 'back_text', 'learned', 
            'created_at', 'updated_at', 'last_reviewed', 'review_count', 
            'next_review', 'days_since_last_review', 'is_due'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'last_reviewed', 
            'review_count', 'next_review', 'user',
            'days_since_last_review', 'is_due'
        ]
    
    def get_days_since_last_review(self, obj):
        """Calcule le nombre de jours depuis la dernière révision."""
        from django.utils import timezone
        if not obj.last_reviewed:
            return None
        
        delta = timezone.now() - obj.last_reviewed
        return delta.days
    
    def get_is_due(self, obj):
        """Détermine si la carte est due pour une révision."""
        from django.utils import timezone
        if not obj.next_review:
            return True  # Jamais révisée, donc due
        
        return obj.next_review <= timezone.now()
    
    def validate(self, data):
        """Validation personnalisée pour les cartes."""
        # Vérifier que les textes ne sont pas vides
        if 'front_text' in data and not data['front_text'].strip():
            raise serializers.ValidationError({"front_text": "Le texte recto ne peut pas être vide."})
        
        if 'back_text' in data and not data['back_text'].strip():
            raise serializers.ValidationError({"back_text": "Le texte verso ne peut pas être vide."})
        
        return data

class FlashcardDeckSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le modèle FlashcardDeck."""
    
    # Ajout d'un champ calculé pour le nombre de cartes
    card_count = serializers.SerializerMethodField()
    # Ajout d'un champ calculé pour le nombre de cartes apprises
    learned_count = serializers.SerializerMethodField()
    # Afficher le nom d'utilisateur au lieu de l'ID
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = FlashcardDeck
        fields = [
            'id', 'name', 'description', 'created_at', 'updated_at', 
            'is_active', 'card_count', 'learned_count', 'username'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'user', 
            'card_count', 'learned_count', 'username'
        ]
    
    def get_card_count(self, obj):
        """Renvoie le nombre total de cartes dans ce deck."""
        return obj.flashcards.count()
    
    def get_learned_count(self, obj):
        """Renvoie le nombre de cartes apprises dans ce deck."""
        return obj.flashcards.filter(learned=True).count()
    
    def get_username(self, obj):
        """Renvoie le nom d'utilisateur du propriétaire du deck."""
        return obj.user.username if obj.user else None
    
    def validate_name(self, value):
        """Valide que le nom du deck n'est pas vide et est unique pour l'utilisateur."""
        if not value.strip():
            raise serializers.ValidationError("Le nom du deck ne peut pas être vide.")
        
        # Vérifier l'unicité du nom pour cet utilisateur
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            # Pour les mises à jour, exclure l'instance actuelle
            instance = getattr(self, 'instance', None)
            queryset = FlashcardDeck.objects.filter(
                user=request.user, 
                name__iexact=value.strip()
            )
            
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
                
            if queryset.exists():
                raise serializers.ValidationError(
                    "Vous avez déjà un deck avec ce nom. Veuillez choisir un nom différent."
                )
        
        return value.strip()

# Sérialiseur pour les opérations de création de deck avec un nombre minimal de champs
class FlashcardDeckCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashcardDeck
        fields = ['id', 'name', 'description', 'is_active']
        read_only_fields = ['id']

# Sérialiseur pour afficher un deck avec ses cartes (utilisé pour les requêtes détaillées)
class FlashcardDeckDetailSerializer(FlashcardDeckSerializer):
    cards = FlashcardSerializer(source='flashcards', many=True, read_only=True)
    
    class Meta(FlashcardDeckSerializer.Meta):
        fields = FlashcardDeckSerializer.Meta.fields + ['cards']