# backend/core/subscription/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .models import UserSubscription, SubscriptionPlan


class SubscriptionMiddleware(MiddlewareMixin):
    """
    Middleware pour vérifier les limitations d'abonnement
    """

    # URLs qui nécessitent un abonnement premium
    PREMIUM_REQUIRED_URLS = [
        '/api/language-ai/premium/',
        '/courses/premium/',
        '/coaching/video/',
        '/certificates/',
    ]

    # URLs qui nécessitent un abonnement pro
    PRO_REQUIRED_URLS = [
        '/api/v1/',  # API access
        '/admin/analytics/',
        '/coaching/private-groups/',
    ]

    def process_request(self, request):
        # Skip pour les admins et certaines URLs
        if (request.user.is_superuser or
            request.path.startswith('/admin/') or
            request.path.startswith('/auth/') or
            request.path.startswith('/static/') or
            request.path.startswith('/media/')):
            return None

        # Skip si utilisateur non connecté
        if not request.user.is_authenticated:
            return None

        # Récupérer ou créer l'abonnement utilisateur
        subscription = self._get_or_create_user_subscription(request.user)

        # Ajouter l'abonnement à la request pour usage dans les vues
        request.user_subscription = subscription

        # Vérifier les limitations basées sur l'URL
        return self._check_url_permissions(request, subscription)

    def _get_or_create_user_subscription(self, user):
        """Récupère ou crée un abonnement gratuit pour l'utilisateur"""
        try:
            return user.subscription
        except UserSubscription.DoesNotExist:
            # Créer un abonnement gratuit par défaut
            free_plan, created = SubscriptionPlan.objects.get_or_create(
                plan_type='free',
                defaults={
                    'name': 'Gratuit',
                    'price_monthly': 0,
                    'max_workspaces': 1,
                    'max_flashcard_decks': 10,
                    'max_ai_conversations_per_month': 50,
                }
            )
            return UserSubscription.objects.create(
                user=user,
                plan=free_plan
            )

    def _check_url_permissions(self, request, subscription):
        """Vérifie les permissions basées sur l'URL demandée"""
        path = request.path

        # Vérifier si l'URL nécessite Pro
        if any(path.startswith(url) for url in self.PRO_REQUIRED_URLS):
            if not subscription.is_pro:
                return self._redirect_to_upgrade(request, 'pro')

        # Vérifier si l'URL nécessite Premium
        elif any(path.startswith(url) for url in self.PREMIUM_REQUIRED_URLS):
            if not subscription.is_premium:
                return self._redirect_to_upgrade(request, 'premium')

        return None

    def _redirect_to_upgrade(self, request, required_plan):
        """Redirige vers la page d'upgrade avec message"""
        if request.path.startswith('/api/'):
            # Pour les APIs, retourner JSON
            return JsonResponse({
                'error': 'Abonnement requis',
                'message': f'Cette fonctionnalité nécessite un abonnement {required_plan.title()}',
                'required_plan': required_plan,
                'upgrade_url': '/subscription/upgrade/'
            }, status=403)
        else:
            # Pour les pages web
            messages.warning(
                request,
                f"Cette fonctionnalité nécessite un abonnement {required_plan.title()}. "
                f"Upgradez votre compte pour continuer!"
            )
            return redirect('/subscription/upgrade/')


class UsageLimitMiddleware(MiddlewareMixin):
    """
    Middleware pour tracker et limiter l'usage des fonctionnalités payantes
    """

    def process_request(self, request):
        # Skip si pas d'utilisateur connecté
        if not request.user.is_authenticated:
            return None

        # Skip pour certaines URLs
        if (request.path.startswith('/admin/') or
            request.path.startswith('/auth/') or
            request.path.startswith('/static/')):
            return None

        # Récupérer l'abonnement
        try:
            subscription = request.user.subscription
        except UserSubscription.DoesNotExist:
            return None

        # Vérifier les limites pour les endpoints IA
        if request.path.startswith('/api/language-ai/chat/'):
            if not subscription.can_use_ai_chat():
                return self._usage_limit_response(request, 'IA conversationnelle')

        return None

    def _usage_limit_response(self, request, feature_name):
        """Retourne une réponse de limite d'usage atteinte"""
        if request.path.startswith('/api/'):
            # Pour les APIs, retourner JSON
            return JsonResponse({
                'error': 'Limite d\'usage atteinte',
                'message': f'Vous avez atteint votre limite mensuelle pour {feature_name}',
                'upgrade_url': '/subscription/upgrade/'
            }, status=429)
        else:
            # Pour les pages web, rediriger
            messages.warning(
                request,
                f"Vous avez atteint votre limite mensuelle pour {feature_name}. "
                f"Upgradez votre compte pour continuer!"
            )
            return redirect('/subscription/upgrade/')