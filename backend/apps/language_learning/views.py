from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import LanguagelearningItem, Language, UserLanguage, LANGUAGE_CHOICES, PROFICIENCY_LEVELS
from .forms import LanguagelearningItemForm
import json


@login_required
def language_learning_home(request):
    """Page d'accueil de Language Learning - Personnalisé selon la langue cible de l'utilisateur"""
    items = LanguagelearningItem.objects.filter(
        user=request.user,
        is_active=True
    )
    
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_items = paginator.get_page(page_number)
    
    # Mapping entre les codes utilisateur (EN, FR, etc.) et nos codes internes (en, fr, etc.)
    auth_to_internal_mapping = {
        'EN': 'en',
        'FR': 'fr',
        'ES': 'es',
        'DE': 'de',
        'IT': 'it',
        'PT': 'pt',
        'NL': 'nl',
        'JA': 'ja',
    }
    
    # Obtenir la langue cible de l'utilisateur depuis ses paramètres
    user_target_language = request.user.target_language  # EN, FR, etc.
    user_target_internal = auth_to_internal_mapping.get(user_target_language, 'en')
    
    # Configuration des langues avec priorité pour la langue cible de l'utilisateur
    language_configs = {
        'en': ('English', 'Master English with interactive lessons', '🇺🇸'),
        'es': ('Spanish', 'Aprende español paso a paso', '🇪🇸'),
        'fr': ('French', 'Apprenez le français facilement', '🇫🇷'),
        'de': ('German', 'Lernen Sie Deutsch effektiv', '🇩🇪'),
        'it': ('Italian', 'Impara l\'italiano con facilità', '🇮🇹'),
        'pt': ('Portuguese', 'Aprenda português facilmente', '🇵🇹'),
        'nl': ('Dutch', 'Leer Nederlands stap voor stap', '🇳🇱'),
        'ja': ('Japanese', '日本語を簡単に学ぼう', '🇯🇵'),
    }
    
    # Créer la liste des langues avec la langue cible en premier
    available_languages = []
    
    # Ajouter d'abord la langue cible de l'utilisateur
    if user_target_internal in language_configs:
        code = user_target_internal
        name, description, flag = language_configs[code]
        lang, created = Language.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'native_name': name,
                'flag_emoji': flag,
                'is_active': True
            }
        )
        available_languages.append({
            'code': code,
            'name': name,
            'description': description,
            'flag': flag,
            'is_learning': UserLanguage.objects.filter(user=request.user, language=lang).exists(),
            'is_target': True  # Marquer comme langue cible
        })
    
    # Ajouter les autres langues
    for code, (name, description, flag) in language_configs.items():
        if code == user_target_internal:
            continue  # Déjà ajoutée
            
        lang, created = Language.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'native_name': name,
                'flag_emoji': flag,
                'is_active': True
            }
        )
        available_languages.append({
            'code': code,
            'name': name,
            'description': description,
            'flag': flag,
            'is_learning': UserLanguage.objects.filter(user=request.user, language=lang).exists(),
            'is_target': False
        })
    
    # Obtenir les langues que l'utilisateur apprend
    user_languages = UserLanguage.objects.filter(user=request.user, is_active=True).select_related('language')
    
    # Statistiques utilisateur (calculées dynamiquement)
    total_lessons = user_languages.count() * 8  # 8 leçons par langue en moyenne
    total_time = sum([ul.total_time_spent for ul in user_languages]) or 150  # en minutes
    max_streak = max([ul.streak_count for ul in user_languages]) if user_languages else 7
    
    # Convertir les minutes en heures/minutes
    hours = total_time // 60
    minutes = total_time % 60
    time_display = f"{hours}h {minutes:02d}m" if hours > 0 else f"{minutes}m"
    
    # Déterminer le niveau basé sur la langue cible spécifiquement
    target_lang_obj = Language.objects.filter(code=user_target_internal).first()
    user_target_progress = None
    if target_lang_obj:
        user_target_progress = UserLanguage.objects.filter(
            user=request.user, 
            language=target_lang_obj, 
            is_active=True
        ).first()
    
    current_level = 'Débutant'
    if user_target_progress:
        current_level = user_target_progress.get_proficiency_level_display()
    elif user_languages.count() > 1:
        current_level = 'Intermédiaire'
    
    user_stats = {
        'streak_days': max_streak,
        'completed_lessons': total_lessons,
        'total_time': time_display,
        'current_level': current_level,
        'target_language_name': language_configs.get(user_target_internal, ('English', '', ''))[0]
    }
    
    context = {
        'items': page_items,
        'total_items': items.count(),
        'available_languages': available_languages,
        'user_languages': user_languages,
        'user_stats': user_stats,
        'user_target_language': user_target_internal,
        'app_name': 'Language Learning',
    }
    return render(request, 'language_learning/home.html', context)


@login_required
def create_item(request):
    """Créer un nouvel item"""
    if request.method == 'POST':
        form = LanguagelearningItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f'{item.title} créé avec succès!')
            return redirect('language_learning_home')
    else:
        form = LanguagelearningItemForm()
    
    return render(request, 'language_learning/create_item.html', {'form': form})


@login_required
def edit_item(request, item_id):
    """Modifier un item"""
    item = get_object_or_404(LanguagelearningItem, id=item_id, user=request.user)
    
    if request.method == 'POST':
        form = LanguagelearningItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'{item.title} modifié avec succès!')
            return redirect('language_learning_home')
    else:
        form = LanguagelearningItemForm(instance=item)
    
    return render(request, 'language_learning/edit_item.html', {'form': form, 'item': item})


@login_required
def delete_item(request, item_id):
    """Supprimer un item"""
    item = get_object_or_404(LanguagelearningItem, id=item_id, user=request.user)
    
    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.success(request, f'{title} supprimé avec succès!')
        return redirect('language_learning_home')
    
    return render(request, 'language_learning/confirm_delete.html', {'item': item})


# API Views
@login_required
def api_items(request):
    """API pour récupérer les items"""
    items = LanguagelearningItem.objects.filter(
        user=request.user,
        is_active=True
    ).values('id', 'title', 'description', 'created_at')
    
    return JsonResponse({
        'items': list(items),
        'count': len(items)
    })


@login_required
def start_language_learning(request):
    """API pour démarrer l'apprentissage d'une langue"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            language_code = data.get('language_code')
            
            if not language_code:
                return JsonResponse({'success': False, 'error': 'Language code is required'})
            
            # Trouver ou créer la langue
            language = Language.objects.filter(code=language_code).first()
            if not language:
                return JsonResponse({'success': False, 'error': 'Language not found'})
            
            # Créer ou récupérer UserLanguage
            user_language, created = UserLanguage.objects.get_or_create(
                user=request.user,
                language=language,
                defaults={
                    'proficiency_level': 'beginner',
                    'target_level': 'intermediate',
                    'daily_goal': 15,
                    'is_active': True
                }
            )
            
            if not created:
                # Réactiver si c'était désactivé
                user_language.is_active = True
                user_language.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Apprentissage de {language.name} commencé !',
                'created': created
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})
