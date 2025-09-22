import os
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import translation

def lms_info(request):
    """Page d'information sur le LMS"""
    context = {
        'lms_url': 'http://127.0.0.1:8001' if settings.DEBUG else '/lms/',
        'is_dev': settings.DEBUG
    }
    return render(request, 'core/lms_info.html', context)

@api_view(['POST'])
@permission_classes([AllowAny])
def contact_view(request):
    """
    Endpoint pour envoyer un email à partir du formulaire de contact.
    """
    data = request.data
    name = data.get('name')
    email = data.get('email')
    subject = data.get('subject')
    message = data.get('message')
    recipient = data.get('recipient', os.getenv('DEFAULT_CONTACT_EMAIL', settings.DEFAULT_FROM_EMAIL))

    # Validation des données
    if not all([name, email, subject, message]):
        return Response(
            {'error': 'Missing required fields'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Préparation du contenu de l'email
        email_subject = f"[Linguify Contact] {subject}"
        email_message = f"""
        Nouveau message du formulaire de contact Linguify:
        
        Nom: {name}
        Email: {email}
        Sujet: {subject}
        
        Message:
        {message}
        """

        # Envoi de l'email
        send_mail(
            email_subject,
            email_message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
            reply_to=[email],
        )
        
        return Response(
            {'message': 'Your message has been sent successfully!'},
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        # Log l'erreur pour le débogage
        print(f"Error sending email: {str(e)}")
        
        return Response(
            {'error': 'Failed to send your message. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def get_preferred_language(request):
    """Get user's preferred language from Accept-Language header or default to 'en'"""
    from django.conf import settings
    
    try:
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            accept_language = request.META['HTTP_ACCEPT_LANGUAGE']
            # Get supported language codes from Django settings
            supported_languages = [lang_code for lang_code, lang_name in settings.LANGUAGES]
            for lang in accept_language.split(','):
                lang_code = lang.strip().split(';')[0].split('-')[0]
                if lang_code in supported_languages:
                    return lang_code
    except (AttributeError, IndexError, ValueError):
        # Handle malformed Accept-Language headers gracefully
        pass
    
    # Return the first language in LANGUAGES as default, or 'en' if not configured
    default_language = settings.LANGUAGES[0][0] if settings.LANGUAGES else 'en'
    return default_language


def language_redirect_view(request, path):
    """Redirect to the same path with language prefix"""
    return redirect(f'/{get_preferred_language(request)}/{path}')


def app_language_redirect_view(request, app_slug):
    """Redirect app URLs to the same URL with language prefix"""
    return redirect(f'/{get_preferred_language(request)}/apps/{app_slug}/')


def smart_home_redirect(request):
    """
    Smart home redirect that avoids multiple redirections:
    - If authenticated → redirect to dashboard
    - If anonymous → redirect directly to login with language prefix
    """
    if request.user.is_authenticated:
        # User is logged in, go to dashboard
        return redirect('/dashboard/')
    else:
        # User is not logged in, redirect directly to localized login
        # Get current language code
        language = translation.get_language() or get_preferred_language(request)

        # Build the localized login URL
        login_url = f'/{language}/auth/login/'
        return redirect(login_url)