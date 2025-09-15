#!/usr/bin/env python
"""
Script pour créer une nouvelle notification de test avec URL d'action
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
from django.utils import timezone
from apps.notification.models import Notification, NotificationType, NotificationPriority

User = get_user_model()

def create_test_notification():
    """Crée une nouvelle notification de test avec redirection"""

    # Utiliser l'utilisateur linguify.info@gmail.com
    try:
        user = User.objects.get(email='linguify.info@gmail.com')
        print(f"✓ Utilisateur trouvé : {user.username} ({user.email})")
    except User.DoesNotExist:
        print("❌ Utilisateur linguify.info@gmail.com non trouvé")
        return False

    print("\n" + "=" * 70)
    print("🔔 CRÉATION NOTIFICATION DE TEST AVEC REDIRECTION")
    print("=" * 70)

    # Créer une nouvelle notification
    portal_url = getattr(settings, 'PORTAL_URL', 'http://localhost:8080')
    terms_url = f"{portal_url}/annexes/terms"

    # Déterminer le message selon la langue
    lang = user.interface_language
    if lang == 'fr':
        title = "🚨 TEST - Action Requise"
        message = "Cliquez ici pour accepter les conditions d'utilisation (TEST)"
    elif lang == 'nl':
        title = "🚨 TEST - Actie Vereist"
        message = "Klik hier om de gebruiksvoorwaarden te accepteren (TEST)"
    elif lang == 'es':
        title = "🚨 TEST - Acción Requerida"
        message = "Haz clic aquí para aceptar los términos de uso (TEST)"
    else:  # en
        title = "🚨 TEST - Action Required"
        message = "Click here to accept the terms of use (TEST)"

    notification = Notification.objects.create(
        user=user,
        type='action_required',
        title=title,
        message=message,
        priority='high',
        data={
            'action': 'accept_terms',
            'action_url': terms_url,
            'test': True,
            'created_by': 'test_script',
            'timestamp': timezone.now().isoformat()
        },
        is_read=False
    )

    print(f"✅ Notification créée avec succès!")
    print(f"\n📋 Détails de la notification:")
    print(f"  • ID: {notification.id}")
    print(f"  • Titre: {notification.title}")
    print(f"  • Message: {notification.message}")
    print(f"  • Type: {notification.type}")
    print(f"  • Priorité: {notification.priority}")
    print(f"  • Non lue: ✓")
    print(f"\n📦 Données JSON:")
    for key, value in notification.data.items():
        print(f"  • {key}: {value}")

    print("\n" + "=" * 70)
    print("🧪 TEST DE REDIRECTION")
    print("=" * 70)
    print("\n1. Connectez-vous avec:")
    print(f"   • Email: {user.email}")
    print(f"   • Mot de passe: TestPassword123!")

    print("\n2. Cliquez sur l'icône cloche 🔔")

    print("\n3. Cliquez sur la notification de test:")
    print(f"   '{title}'")

    print("\n4. Vous devriez être redirigé vers:")
    print(f"   {terms_url}")

    print("\n5. Vérifiez la console du navigateur (F12) pour:")
    print("   • [NotificationHeader] Terms notification clicked")
    print("   • [NotificationHeader] Notification data")
    print("   • [NotificationHeader] Redirecting to: " + terms_url)

    print("\n💡 Si la redirection ne fonctionne pas:")
    print("   1. Videz le cache du navigateur (Ctrl+F5)")
    print("   2. Vérifiez que le fichier JS est à jour")
    print("   3. Regardez les erreurs dans la console")

    # Afficher les dernières notifications
    print("\n" + "=" * 70)
    print("📊 DERNIÈRES NOTIFICATIONS NON LUES")
    print("=" * 70)

    unread = Notification.objects.filter(
        user=user,
        is_read=False
    ).order_by('-created_at')[:5]

    for notif in unread:
        time = notif.created_at.strftime('%H:%M:%S')
        has_url = '✓' if (notif.data and 'action_url' in notif.data) else '✗'
        print(f"🔵 [{time}] {notif.title[:40]} - URL: {has_url}")

    return True

if __name__ == "__main__":
    print("🚀 Open Linguify - Création Notification Test")
    print("=" * 70)

    success = create_test_notification()

    if success:
        print("\n✨ Notification de test créée avec succès!")
    else:
        print("\n⚠️ Échec de la création")
        sys.exit(1)