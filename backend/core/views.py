from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect

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
    recipient = data.get('recipient', 'linguify.info@gmail.com')

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
    if 'HTTP_ACCEPT_LANGUAGE' in request.META:
        accept_language = request.META['HTTP_ACCEPT_LANGUAGE']
        supported_languages = ['en', 'fr', 'es', 'nl']
        for lang in accept_language.split(','):
            lang_code = lang.strip().split(';')[0].split('-')[0]
            if lang_code in supported_languages:
                return lang_code
    return 'en'


def language_redirect_view(request, path):
    """Redirect to the same path with language prefix"""
    return redirect(f'/{get_preferred_language(request)}/{path}')


def app_language_redirect_view(request, app_slug):
    """Redirect app URLs to the same URL with language prefix"""
    return redirect(f'/{get_preferred_language(request)}/apps/{app_slug}/')