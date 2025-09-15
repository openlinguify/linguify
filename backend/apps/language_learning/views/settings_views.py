from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@login_required
def language_learning_settings(request):
    """View for language learning specific settings"""
    if request.method == 'POST':
        user = request.user

        # Update language preferences
        native_language = request.POST.get('native_language')
        target_language = request.POST.get('target_language')
        language_level = request.POST.get('language_level')
        objectives = request.POST.get('objectives')

        # Validate languages are different
        if native_language == target_language:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Native and target languages must be different'
                })
            messages.error(request, 'Native and target languages must be different')
            return render(request, 'language_learning/settings.html', {'user': user})

        # Update user fields
        if native_language:
            user.native_language = native_language
        if target_language:
            user.target_language = target_language
        if language_level:
            user.language_level = language_level
        if objectives:
            user.objectives = objectives

        user.save()

        # Handle AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Settings saved successfully!'
            })

        messages.success(request, 'Settings saved successfully!')
        return redirect('language_learning:settings')

    return render(request, 'language_learning/language_learning_settings.html', {
        'user': request.user
    })