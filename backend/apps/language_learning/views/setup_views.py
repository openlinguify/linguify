"""
Vues pour la configuration initiale du profil d'apprentissage
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from ..forms import QuickSetupForm, UserLearningProfileForm
from ..models import UserLearningProfile


@login_required
@require_http_methods(["GET", "POST"])
def learning_setup(request):
    """
    Vue pour la configuration initiale du profil d'apprentissage
    Utilisée après l'inscription pour configurer les préférences d'apprentissage
    """
    user = request.user

    # Vérifier si l'utilisateur a déjà un profil d'apprentissage configuré
    try:
        profile = user.learning_profile
        if profile.native_language != 'EN' or profile.target_language != 'FR':
            # L'utilisateur a déjà configuré son profil, rediriger vers le dashboard
            return redirect('saas_web:dashboard')
    except UserLearningProfile.DoesNotExist:
        # Créer un profil par défaut si il n'existe pas
        profile = UserLearningProfile.objects.create(user=user)

    if request.method == 'POST':
        form = QuickSetupForm(request.POST)
        if form.is_valid():
            # Mettre à jour le profil d'apprentissage
            profile.native_language = form.cleaned_data['native_language']
            profile.target_language = form.cleaned_data['target_language']
            profile.language_level = form.cleaned_data['language_level']
            profile.objectives = form.cleaned_data['objectives']
            profile.save()

            messages.success(request, _('Your learning profile has been configured successfully!'))

            # Rediriger vers le dashboard ou une page d'accueil
            return redirect('saas_web:dashboard')
    else:
        # Pré-remplir le formulaire avec les données existantes
        initial_data = {
            'native_language': profile.native_language,
            'target_language': profile.target_language,
            'language_level': profile.language_level,
            'objectives': profile.objectives,
        }
        form = QuickSetupForm(initial=initial_data)

    context = {
        'form': form,
        'title': _('Configure your learning preferences'),
        'subtitle': _('Tell us about your language learning goals to personalize your experience'),
        'user': user,
    }

    return render(request, 'language_learning/setup.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def profile_settings(request):
    """
    Vue pour modifier les paramètres complets du profil d'apprentissage
    """
    user = request.user

    try:
        profile = user.learning_profile
    except UserLearningProfile.DoesNotExist:
        profile = UserLearningProfile.objects.create(user=user)

    if request.method == 'POST':
        form = UserLearningProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your learning settings have been updated successfully!'))

            # Si c'est une requête AJAX, retourner JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': str(_('Settings updated successfully!'))})

            return redirect('language_learning:profile_settings')
    else:
        form = UserLearningProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
        'title': _('Learning Settings'),
        'subtitle': _('Customize your language learning experience'),
    }

    return render(request, 'language_learning/profile_settings.html', context)


@login_required
def skip_setup(request):
    """
    Permet de passer la configuration initiale
    """
    if request.method == 'POST':
        return redirect('saas_web:dashboard')
    return redirect('language_learning:learning_setup')