"""
Vues pour le frontend web intégré de Linguify
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from apps.authentication.models import User as CustomUser
from django.db import IntegrityError
import json


def landing_page(request):
    """
    Page d'accueil principale multilingue de Linguify
    """
    from django.utils.translation import gettext as _
    
    # Gestion de la langue via paramètre GET
    language = request.GET.get('language')
    if language and language in ['fr', 'en', 'es', 'nl']:
        from django.utils import translation
        translation.activate(language)
        request.session[translation.LANGUAGE_SESSION_KEY] = language
    
    # Définir les textes traduits pour éviter les problèmes d'apostrophes
    context = {
        'page_title': _("Linguify - Apprendre les langues avec l'IA"),
        'page_description': _("Linguify vous aide à apprendre les langues grâce à l'intelligence artificielle. Cours personnalisés, exercices interactifs et suivi de progression."),
        'page_keywords': _("apprentissage langues, IA, intelligence artificielle, cours personnalisés, flashcards, notebook"),
    }
    
    return render(request, 'frontend/landing_simple.html', context)


def features_page(request):
    """
    Page des fonctionnalités détaillées
    """
    # Gestion de la langue via paramètre GET
    language = request.GET.get('language')
    if language and language in ['fr', 'en', 'es', 'nl']:
        from django.utils import translation
        translation.activate(language)
        request.session[translation.LANGUAGE_SESSION_KEY] = language
    
    return render(request, 'frontend/features.html')


def set_language(request, language):
    """
    Vue pour changer la langue de l'interface
    """
    from django.utils import translation
    from django.shortcuts import redirect
    
    if language in ['fr', 'en', 'es', 'nl']:
        translation.activate(language)
        request.session[translation.LANGUAGE_SESSION_KEY] = language
    
    # Rediriger vers la page de référence ou la page d'accueil
    next_page = request.META.get('HTTP_REFERER', '/')
    return redirect(next_page)


def login_view(request):
    """
    Page de connexion
    """
    if request.user.is_authenticated:
        return redirect('frontend_web:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Configurer la durée de session
            if not remember:
                request.session.set_expiry(0)  # Session expire à la fermeture du navigateur
            
            messages.success(request, f'Bienvenue, {user.first_name or user.username} !')
            
            # Rediriger vers la page demandée ou le dashboard
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'auth/login.html')


def register_view(request):
    """
    Page d'inscription
    """
    if request.user.is_authenticated:
        return redirect('frontend_web:dashboard')
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        target_language = request.POST.get('target_language')
        
        # Validation de base
        if password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'auth/register.html')
        
        if len(password1) < 8:
            messages.error(request, 'Le mot de passe doit contenir au moins 8 caractères.')
            return render(request, 'auth/register.html')
        
        try:
            # Créer l'utilisateur
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                target_language=target_language
            )
            
            # Connecter automatiquement l'utilisateur
            login(request, user)
            
            messages.success(request, f'Compte créé avec succès ! Bienvenue, {first_name} !')
            return redirect('frontend_web:dashboard')
            
        except IntegrityError:
            messages.error(request, 'Ce nom d\'utilisateur ou email est déjà utilisé.')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création du compte : {str(e)}')
    
    return render(request, 'auth/register.html')


def logout_view(request):
    """
    Déconnexion
    """
    logout(request)
    messages.success(request, 'Vous êtes maintenant déconnecté.')
    return redirect('frontend_web:landing')


@login_required
def dashboard_view(request):
    """
    Dashboard principal avec la liste des applications
    """
    # Récupérer les statistiques de l'utilisateur
    stats = {
        'lessons_completed': 12,  # À remplacer par de vraies données
        'study_streak': 7,
        'vocabulary_learned': 156,
        'total_time': '24h'
    }
    
    # Récupérer les notifications non lues
    from apps.notification.models import Notification
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:10]  # Limiter à 10 notifications
    
    context = {
        'stats': stats,
        'user': request.user,
        'notifications': notifications,
        'unread_count': notifications.count()
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def profile_view(request):
    """
    Page de profil utilisateur
    """
    if request.method == 'POST':
        # Logique pour mettre à jour le profil
        pass
    
    return render(request, 'auth/profile.html')


@login_required
def settings_view(request):
    """
    Page de paramètres utilisateur
    """
    # Safely get profile picture URL
    profile_picture_url = None
    try:
        if request.user.profile_picture:
            profile_picture_url = request.user.profile_picture.url
    except ValueError:
        # Handle case where profile_picture field has no file
        profile_picture_url = None
    
    context = {
        'page_title': 'Paramètres',
        'user_data': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        },
        'user': request.user,
        'profile_picture_url': profile_picture_url
    }
    
    return render(request, 'authentication/settings/dashboard-style.html', context)


@login_required
@require_http_methods(["GET"])
def get_user_stats(request):
    """
    API pour récupérer les statistiques utilisateur
    """
    # Ici vous pouvez calculer les vraies statistiques
    stats = {
        'lessons_completed': 12,
        'study_streak': 7,
        'vocabulary_learned': 156,
        'total_time_minutes': 1440,  # 24 heures en minutes
        'current_level': 'Intermédiaire',
        'next_lesson': 'Les verbes irréguliers',
        'weekly_goal_progress': 75,  # Pourcentage
    }
    
    return JsonResponse(stats)


@login_required
@require_http_methods(["GET"])
def get_available_apps(request):
    """
    API pour récupérer la liste des applications disponibles depuis le système d'apps
    """
    from app_manager.models import App, UserAppSettings
    
    # Récupérer les apps depuis le système
    user_settings, created = UserAppSettings.objects.get_or_create(user=request.user)
    if created:
        # Si nouvellement créé, activer toutes les apps par défaut
        all_apps = App.objects.filter(is_enabled=True)
        user_settings.enabled_apps.set(all_apps)
    
    # Récupérer les apps actives pour l'utilisateur
    enabled_apps = user_settings.enabled_apps.filter(is_enabled=True).order_by('order', 'display_name')
    
    # Mapper les données pour le frontend
    apps_data = []
    for app in enabled_apps:
        # Déterminer l'URL en fonction du manifest
        frontend_route = app.manifest_data.get('frontend_components', {}).get('route', '')
        web_url = app.manifest_data.get('technical_info', {}).get('web_url', '')
        
        # Préférer l'URL web OWL si disponible
        app_url = web_url or frontend_route or f'/{app.name}/'
        
        # Mapper les icônes
        icon_mapping = {
            '📓': 'bi-journal-text',
            '📚': 'bi-book',
            '🃏': 'bi-collection',
            '🤖': 'bi-robot',
            '📊': 'bi-graph-up',
            '🎯': 'bi-bullseye',
        }
        
        icon = app.manifest_data.get('frontend_components', {}).get('icon', '')
        bootstrap_icon = icon_mapping.get(icon, 'bi-app')
        
        # Déterminer le statut
        status = 'active'
        if 'beta' in app.display_name.lower() or 'bêta' in app.display_name.lower():
            status = 'beta'
        elif 'soon' in app.display_name.lower() or 'bientôt' in app.display_name.lower():
            status = 'coming_soon'
            
        # Couleurs par app
        color_mapping = {
            'notebook': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'cours': 'linear-gradient(135deg, #4ade80 0%, #3b82f6 100%)',
            'révision': 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
            'revision': 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
            'ia': 'linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%)',
            'progression': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            'quiz': 'linear-gradient(135deg, #ec4899 0%, #f43f5e 100%)',
        }
        
        color = color_mapping.get(app.display_name.lower(), 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)')
        
        apps_data.append({
            'id': app.code,
            'name': app.display_name,
            'description': app.manifest_data.get('frontend_components', {}).get('description', app.description),
            'icon': bootstrap_icon,
            'url': app_url,
            'status': status,
            'category': app.category.lower().replace(' ', '_'),
            'color': color
        })
    
    return JsonResponse({'apps': apps_data})


@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """
    API pour récupérer les notifications de l'utilisateur
    """
    from apps.notification.models import Notification
    
    # Récupérer les notifications non lues
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:20]  # Limiter à 20 notifications
    
    notifications_data = []
    for notification in notifications:
        # Formater la date
        import datetime
        from django.utils import timezone
        
        now = timezone.now()
        diff = now - notification.created_at
        
        if diff.days > 0:
            time_str = f"Il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            time_str = f"Il y a {hours} heure{'s' if hours > 1 else ''}"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            time_str = f"Il y a {minutes} minute{'s' if minutes > 1 else ''}"
        else:
            time_str = "À l'instant"
        
        # Déterminer l'icône et la couleur selon le type
        type_config = {
            'terms': {'icon': 'bi-exclamation-triangle', 'color': 'danger'},
            'system': {'icon': 'bi-gear', 'color': 'primary'},
            'achievement': {'icon': 'bi-trophy', 'color': 'success'},
            'lesson_reminder': {'icon': 'bi-book', 'color': 'info'},
            'flashcard': {'icon': 'bi-collection', 'color': 'warning'},
        }
        
        config = type_config.get(notification.type, {'icon': 'bi-bell', 'color': 'secondary'})
        
        notifications_data.append({
            'id': str(notification.id),
            'title': notification.title,
            'message': notification.message,
            'type': notification.type,
            'priority': notification.priority,
            'icon': config['icon'],
            'color': config['color'],
            'time': time_str,
            'data': notification.data or {},
            'created_at': notification.created_at.isoformat()
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': notifications.count()
    })


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """
    Marquer une notification comme lue
    """
    from apps.notification.models import Notification
    
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.is_read = True
        notification.save()
        
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """
    Marquer toutes les notifications comme lues
    """
    from apps.notification.models import Notification
    
    try:
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        
        return JsonResponse({'success': True, 'count': count})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def terms_view(request):
    """
    Page des conditions d'utilisation
    """
    context = {
        'user': request.user if request.user.is_authenticated else None
    }
    return render(request, 'legal/terms.html', context)


@login_required
@require_http_methods(["POST"])
def accept_terms_view(request):
    """
    Accepter les conditions d'utilisation
    """
    from django.utils import timezone
    
    accept_terms = request.POST.get('accept_terms')
    
    if accept_terms:
        try:
            # Mettre à jour l'utilisateur
            request.user.terms_accepted = True
            request.user.terms_accepted_at = timezone.now()
            request.user.save(update_fields=['terms_accepted', 'terms_accepted_at'])
            
            # Marquer toutes les notifications de terms comme lues
            from apps.notification.models import Notification
            Notification.objects.filter(
                user=request.user,
                type='terms',
                is_read=False
            ).update(is_read=True)
            
            messages.success(request, 'Merci d\'avoir accepté les conditions d\'utilisation !')
            return redirect('frontend_web:dashboard')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'acceptation des conditions : {str(e)}')
    else:
        messages.error(request, 'Vous devez accepter les conditions d\'utilisation pour continuer.')
    
    return redirect('frontend_web:terms')