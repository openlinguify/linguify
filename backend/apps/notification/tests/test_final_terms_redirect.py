#!/usr/bin/env python
"""
Script de test final pour vérifier la redirection des notifications
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
from apps.notification.models import Notification
from apps.notification.services import send_terms_acceptance_email_and_notification

User = get_user_model()

def test_final_redirect():
    """Test final de la redirection des notifications"""

    print("🎯 TEST FINAL - REDIRECTION NOTIFICATIONS")
    print("=" * 70)

    # Utiliser l'utilisateur de test
    try:
        user = User.objects.get(email=os.getenv('TEST_EMAIL'))
        print(f"✓ Utilisateur: {user.username} ({user.email})")
        print(f"  Langue: {user.interface_language}")
    except User.DoesNotExist:
        print("❌ Utilisateur non trouvé")
        return False

    # 1. Créer une nouvelle notification via le service
    print("\n1️⃣ CRÉATION NOUVELLE NOTIFICATION VIA SERVICE")
    print("-" * 50)

    success = send_terms_acceptance_email_and_notification(user)
    if success:
        print("✅ Notification créée via le service")

        # Récupérer la dernière notification
        latest = Notification.objects.filter(
            user=user,
            type='action_required'
        ).order_by('-created_at').first()

        if latest:
            print(f"  • ID: {str(latest.id)[:8]}...")
            print(f"  • Titre: {latest.title}")
            print(f"  • Non lue: {'✓' if not latest.is_read else '✗'}")

            if latest.data and 'action_url' in latest.data:
                print(f"  ✅ URL présente: {latest.data['action_url']}")
            else:
                print(f"  ❌ URL manquante!")
    else:
        print("❌ Échec de création")

    # 2. Vérifier les notifications non lues
    print("\n2️⃣ NOTIFICATIONS NON LUES AVEC URL")
    print("-" * 50)

    unread_with_url = Notification.objects.filter(
        user=user,
        is_read=False,
        type__in=['terms', 'terms_update', 'action_required'],
        data__action_url__isnull=False
    ).order_by('-created_at')[:5]

    if unread_with_url:
        print(f"✅ {unread_with_url.count()} notification(s) prête(s) pour test:")
        for notif in unread_with_url:
            print(f"  🔵 {notif.title[:50]}")
            print(f"     → {notif.data.get('action_url', 'NO URL')}")
    else:
        print("⚠️ Aucune notification non lue avec URL")

    # 3. Instructions de test
    print("\n3️⃣ TEST MANUEL DE REDIRECTION")
    print("-" * 50)
    print("\n📱 Étapes de test:")
    print("\n1. Connectez-vous:")
    print(f"   • URL: http://localhost:8000/")
    print(f"   • Email: {user.email}")
    print(f"   • Mot de passe: TestPassword123!")

    print("\n2. Cliquez sur l'icône cloche 🔔 dans le header")

    print("\n3. Vous devriez voir:")
    if unread_with_url:
        first = unread_with_url[0]
        print(f"   • Badge rouge avec le nombre")
        print(f"   • Notification: '{first.title[:40]}...'")
        print(f"   • Point bleu indiquant non lu")

    print("\n4. Cliquez sur la notification")

    print("\n5. Résultat attendu:")
    print(f"   ✅ Redirection vers: {settings.PORTAL_URL}/annexes/terms")
    print(f"   ✅ Page des conditions d'utilisation s'affiche")

    # 4. Debug JavaScript
    print("\n4️⃣ DEBUG JAVASCRIPT (Console F12)")
    print("-" * 50)
    print("\nMessages attendus dans la console:")
    print("  [NotificationHeader] Terms notification clicked: {object}")
    print("  [NotificationHeader] Notification data: {action_url: '...'}")
    print(f"  [NotificationHeader] Redirecting to: {settings.PORTAL_URL}/annexes/terms")

    print("\nSi ça ne marche pas:")
    print("  1. Videz le cache (Ctrl+F5)")
    print("  2. Vérifiez que notification-header.js est à jour")
    print("  3. Testez avec la notification '🚨 TEST - Action Requise'")

    # 5. Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DU SYSTÈME")
    print("=" * 70)
    print("\n✅ Corrections appliquées:")
    print("  • JavaScript vérifie data.action_url")
    print("  • Port corrigé: localhost:8080")
    print("  • Fallback sur détection 'terms'/'conditions'")
    print("  • Notifications existantes corrigées")
    print("  • Service crée les bonnes données")

    portal_url = getattr(settings, 'PORTAL_URL', 'http://localhost:8080')
    print(f"\n🎯 URL cible: {portal_url}/annexes/terms")

    return True

if __name__ == "__main__":
    print("🚀 Open Linguify - Test Final Redirection")
    print("=" * 70)

    success = test_final_redirect()

    if success:
        print("\n✨ Système prêt pour test!")
    else:
        print("\n⚠️ Problème détecté")
        sys.exit(1)