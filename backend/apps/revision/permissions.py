# backend/apps/revision/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS


class FlashcardDeckPermission(BasePermission):
    """
    Permission granulaire pour les decks de flashcards:
    - Lecture: Autorisée pour les decks publics ou propriétaires
    - Écriture: Autorisée uniquement pour les propriétaires
    """
    
    def has_permission(self, request, view):
        """
        Permission au niveau de la vue/action
        """
        # Actions de liste et détail : autorisées pour tous
        if view.action in ['list', 'retrieve', 'stats']:
            return True
            
        # Actions de modification : requièrent une authentification
        if view.action in ['create', 'update', 'partial_update', 'destroy', 
                          'toggle_public', 'archive_management', 'batch_delete']:
            return request.user.is_authenticated
            
        # Actions personnalisées : requièrent une authentification par défaut
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Permission au niveau de l'objet
        """
        # Lecture : autorisée si le deck est public ou si l'utilisateur en est propriétaire
        if request.method in SAFE_METHODS:
            return obj.is_public or (request.user.is_authenticated and obj.user == request.user)
        
        # Écriture : autorisée uniquement pour le propriétaire
        return request.user.is_authenticated and obj.user == request.user


class FlashcardPermission(BasePermission):
    """
    Permission pour les flashcards individuelles:
    - Lecture: Autorisée si la carte appartient à un deck public ou à l'utilisateur
    - Écriture: Autorisée uniquement pour le propriétaire
    """
    
    def has_permission(self, request, view):
        """
        Permission au niveau de la vue/action
        """
        # Actions de liste et détail : autorisées pour tous
        if view.action in ['list', 'retrieve']:
            return True
            
        # Actions de modification : requièrent une authentification
        if view.action in ['create', 'update', 'partial_update', 'destroy', 
                          'toggle_learned', 'batch_delete', 'review']:
            return request.user.is_authenticated
            
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Permission au niveau de l'objet
        """
        # Lecture : autorisée si le deck parent est public ou si l'utilisateur en est propriétaire
        if request.method in SAFE_METHODS:
            return (obj.deck.is_public and not obj.deck.is_archived) or \
                   (request.user.is_authenticated and obj.user == request.user)
        
        # Écriture : autorisée uniquement pour le propriétaire
        return request.user.is_authenticated and obj.user == request.user


class IsOwnerOrReadOnlyPublic(BasePermission):
    """
    Permission simple : propriétaire pour écriture, lecture publique autorisée
    """
    
    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour tous si l'objet est public
        if request.method in SAFE_METHODS:
            return getattr(obj, 'is_public', False) or \
                   (request.user.is_authenticated and obj.user == request.user)
        
        # Permissions d'écriture uniquement pour le propriétaire
        return request.user.is_authenticated and obj.user == request.user


class DeckBatchPermission(BasePermission):
    """
    Permission pour les opérations par lot sur les decks
    """
    
    def has_permission(self, request, view):
        """
        Les opérations par lot requièrent une authentification
        """
        return request.user.is_authenticated
    
    def validate_deck_ownership(self, user, deck_ids):
        """
        Valide que l'utilisateur est propriétaire de tous les decks spécifiés
        
        Args:
            user: L'utilisateur effectuant l'opération
            deck_ids: Liste des IDs de decks à vérifier
            
        Returns:
            tuple: (is_valid, error_message)
        """
        from .models import FlashcardDeck
        
        if not deck_ids:
            return False, "Aucun deck spécifié"
        
        if len(deck_ids) > 100:  # Limite de sécurité
            return False, "Trop de decks sélectionnés (maximum 100)"
        
        # Vérifier que tous les decks appartiennent à l'utilisateur
        user_deck_count = FlashcardDeck.objects.filter(
            id__in=deck_ids,
            user=user
        ).count()
        
        if user_deck_count != len(deck_ids):
            return False, "Vous n'êtes pas autorisé à modifier certains de ces decks"
        
        return True, None


class RateLimitPermission(BasePermission):
    """
    Permission pour limiter le taux de requêtes (rate limiting basique)
    """
    
    # Cache simple en mémoire (pour production, utiliser Redis)
    _requests_cache = {}
    
    def has_permission(self, request, view):
        """
        Limite le nombre de requêtes par utilisateur/IP
        """
        # Limites par action
        limits = {
            'create': (10, 300),  # 10 créations par 5 minutes
            'batch_delete': (5, 300),  # 5 suppressions par lot par 5 minutes
            'import': (3, 300),  # 3 imports par 5 minutes
        }
        
        action = getattr(view, 'action', None)
        if action not in limits:
            return True
        
        max_requests, window = limits[action]
        
        # Identifier l'utilisateur/IP
        identifier = str(request.user.id) if request.user.is_authenticated else request.META.get('REMOTE_ADDR')
        cache_key = f"{identifier}:{action}"
        
        import time
        current_time = time.time()
        
        # Nettoyer les anciennes entrées
        if cache_key in self._requests_cache:
            self._requests_cache[cache_key] = [
                timestamp for timestamp in self._requests_cache[cache_key]
                if current_time - timestamp < window
            ]
        else:
            self._requests_cache[cache_key] = []
        
        # Vérifier la limite
        if len(self._requests_cache[cache_key]) >= max_requests:
            return False
        
        # Enregistrer cette requête
        self._requests_cache[cache_key].append(current_time)
        return True
    
    def get_error_message(self):
        return "Trop de requêtes. Veuillez patienter avant de réessayer."