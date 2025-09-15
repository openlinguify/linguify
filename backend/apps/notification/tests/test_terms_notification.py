#!/usr/bin/env python
"""
Script pour envoyer une notification de conditions d'utilisation
"""
import os
import sys
import django

# Remonter au répertoire backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.conf import settings
from apps.notification.services import send_terms_acceptance_email_and_notification
from apps.notification.models import Notification

User = get_user_model()

def send_terms_notification():
    """Envoie une notification et email de conditions d'utilisation"""

    # Utiliser l'utilisateur linguify.info@gmail.com
    try:
        user = User.objects.get(email='linguify.info@gmail.com')
        print(f"✓ Utilisateur trouvé : {user.username} ({user.email})")
        print(f"  Langue d'interface : {user.interface_language}")
    except User.DoesNotExist:
        print("❌ Utilisateur linguify.info@gmail.com non trouvé")
        return False

    print("\n" + "=" * 70)
    print("📜 ENVOI NOTIFICATION CONDITIONS D'UTILISATION")
    print("=" * 70)

    # Envoyer la notification et l'email
    print("\n📤 Envoi de la notification et email...")
    try:
        success = send_terms_acceptance_email_and_notification(user)

        if success:
            print("✅ Notification et email envoyés avec succès!")

            # Récupérer la notification créée
            latest_notification = Notification.objects.filter(
                user=user,
                type='action_required'
            ).order_by('-created_at').first()

            if latest_notification:
                print(f"\n📋 Détails de la notification:")
                print(f"  • ID: {latest_notification.id}")
                print(f"  • Titre: {latest_notification.title}")
                print(f"  • Message: {latest_notification.message[:100]}...")
                print(f"  • Priorité: {latest_notification.priority}")
                print(f"  • Type: {latest_notification.type}")

                # Afficher l'URL d'action
                if latest_notification.data and 'action_url' in latest_notification.data:
                    print(f"  • URL: {latest_notification.data['action_url']}")

                # Traductions selon la langue
                lang = user.interface_language
                if lang == 'fr':
                    print(f"\n🇫🇷 Notification en français:")
                    print(f"  'Action requise : Accepter les Conditions d'Utilisation'")
                elif lang == 'en':
                    print(f"\n🇬🇧 Notification in English:")
                    print(f"  'Action Required: Accept Terms of Use'")
                elif lang == 'nl':
                    print(f"\n🇳🇱 Notificatie in het Nederlands:")
                    print(f"  'Actie vereist: Accepteer de Gebruiksvoorwaarden'")
                elif lang == 'es':
                    print(f"\n🇪🇸 Notificación en español:")
                    print(f"  'Acción requerida: Aceptar los Términos de Uso'")
        else:
            print("❌ Échec de l'envoi")
            return False

    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # Afficher les dernières notifications
    print("\n" + "=" * 70)
    print("📊 DERNIÈRES NOTIFICATIONS DE L'UTILISATEUR")
    print("=" * 70)

    recent_notifications = Notification.objects.filter(
        user=user
    ).order_by('-created_at')[:10]

    for notif in recent_notifications:
        status = "🔵 Non lu" if not notif.is_read else "⚪ Lu"
        time = notif.created_at.strftime('%H:%M:%S')
        print(f"{status} [{time}] {notif.title[:60]}")

    # Instructions
    print("\n" + "=" * 70)
    print("📱 POUR VOIR LA NOTIFICATION")
    print("=" * 70)
    print(f"1. Connectez-vous avec:")
    print(f"   • Email: {user.email}")
    print(f"   • Mot de passe: TestPassword123!")
    print(f"\n2. La notification apparaîtra:")
    print(f"   • Dans l'icône cloche (badge rouge)")
    print(f"   • Dans le centre de notifications")
    print(f"   • Avec un bouton d'action vers: {settings.PORTAL_URL}/annexes/terms")
    print(f"\n3. Un email a aussi été envoyé à {user.email}")

    return True

if __name__ == "__main__":
    print("🚀 Open Linguify - Test Notification Conditions d'Utilisation")
    print("=" * 70)

    success = send_terms_notification()

    if success:
        print("\n✨ Notification et email envoyés avec succès!")
    else:
        print("\n⚠️ Échec de l'envoi")
        sys.exit(1)