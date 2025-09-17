#!/usr/bin/env python
"""
Script de test pour envoyer un email et une notification de conditions d'utilisation
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.notification.services import send_terms_acceptance_email_and_notification
from apps.notification.models import Notification
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

User = get_user_model()

def test_terms_notification_and_email():
    """Envoie un email de test et crée une notification pour les conditions d'utilisation"""

    # Récupérer l'utilisateur
    try:
        test_email = os.getenv('TEST_EMAIL')
        user = User.objects.get(email=test_email)
        print(f"✓ Utilisateur trouvé : {user.username} ({user.email})")
    except User.DoesNotExist:
        print(f"❌ Utilisateur {test_email} non trouvé")
        return False

    # 1. Créer la notification via la fonction combinée
    print("\n📬 Création de la notification et envoi email...")
    try:
        success = send_terms_acceptance_email_and_notification(user)
        if success:
            print(f"✓ Notification et email envoyés avec succès")
        else:
            print("⚠️ Erreur lors de l'envoi")
    except Exception as e:
        print(f"❌ Erreur lors de la création de la notification : {e}")

    # 2. Envoyer l'email de test à l'adresse configurée
    print("\n📧 Envoi de l'email de test...")
    try:
        # Préparer le contexte
        portal_url = getattr(settings, 'PORTAL_URL', 'http://localhost:8080')
        context = {
            'user': user,
            'terms_url': f"{portal_url}/annexes/terms",
            'portal_url': portal_url,
            'app_name': "Open Linguify"
        }

        # Générer le contenu de l'email
        subject = "TEST - Action requise : Accepter les Conditions d'Utilisation"
        html_message = render_to_string('emails/terms_reminder.html', context)
        plain_message = render_to_string('emails/terms_reminder.txt', context)

        # Envoyer l'email
        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[os.getenv('TEST_EMAIL')],
            html_message=html_message,
            fail_silently=False
        )

        if result:
            print(f"✓ Email envoyé avec succès à {os.getenv('TEST_EMAIL')}")
            print(f"  - Sujet: {subject}")
            print(f"  - De: {settings.DEFAULT_FROM_EMAIL}")
            print(f"  - URL des conditions: {context['terms_url']}")
        else:
            print("❌ L'email n'a pas pu être envoyé")

    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email : {e}")
        import traceback
        traceback.print_exc()

    # 3. Afficher les notifications récentes de l'utilisateur
    print(f"\n📋 Notifications récentes pour {user.username}:")
    recent_notifications = Notification.objects.filter(user=user).order_by('-created_at')[:5]
    for notif in recent_notifications:
        status = "🔵 Non lu" if not notif.is_read else "⚪ Lu"
        print(f"  {status} [{notif.created_at.strftime('%H:%M')}] {notif.title}")

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("TEST D'ENVOI EMAIL ET NOTIFICATION - CONDITIONS D'UTILISATION")
    print("=" * 60)

    # Vérifier la configuration email
    print("\n🔧 Configuration email:")
    print(f"  - EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"  - EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"  - EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"  - DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"  - PORTAL_URL: {getattr(settings, 'PORTAL_URL', 'Non défini')}")

    # Exécuter le test
    success = test_terms_notification_and_email()

    if success:
        print("\n✅ Test terminé avec succès!")
    else:
        print("\n❌ Test échoué")
        sys.exit(1)