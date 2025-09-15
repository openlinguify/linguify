#!/usr/bin/env python
"""
Script pour vérifier les données des notifications et leur URL d'action
"""
import os
import sys
import django
import json

# Remonter au répertoire backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.notification.models import Notification

User = get_user_model()

def check_notification_data():
    """Vérifie les données des notifications pour l'utilisateur test"""

    # Utiliser l'utilisateur linguify.info@gmail.com
    try:
        user = User.objects.get(email='linguify.info@gmail.com')
        print(f"✓ Utilisateur trouvé : {user.username} ({user.email})")
    except User.DoesNotExist:
        print("❌ Utilisateur linguify.info@gmail.com non trouvé")
        return False

    print("\n" + "=" * 70)
    print("🔍 VÉRIFICATION DES DONNÉES DE NOTIFICATION")
    print("=" * 70)

    # Récupérer les notifications de type terms/action_required
    terms_notifications = Notification.objects.filter(
        user=user,
        type__in=['terms', 'terms_update', 'action_required']
    ).order_by('-created_at')[:5]

    if not terms_notifications:
        print("❌ Aucune notification de conditions d'utilisation trouvée")
        return False

    for i, notif in enumerate(terms_notifications, 1):
        print(f"\n📋 Notification #{i}")
        print("-" * 50)
        print(f"  ID: {notif.id}")
        print(f"  Type: {notif.type}")
        print(f"  Titre: {notif.title}")
        print(f"  Message: {notif.message[:100]}...")
        print(f"  Priorité: {notif.priority}")
        print(f"  Non lu: {'✓' if not notif.is_read else '✗'}")
        print(f"  Créée: {notif.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # Vérifier les données JSON
        print(f"\n  📦 Données JSON:")
        if notif.data:
            try:
                # Afficher les données formatées
                for key, value in notif.data.items():
                    print(f"    • {key}: {value}")

                # Vérifier spécifiquement action_url
                if 'action_url' in notif.data:
                    print(f"\n  ✅ URL d'action trouvée: {notif.data['action_url']}")
                else:
                    print(f"\n  ⚠️ Pas d'URL d'action dans les données")
                    print(f"     → L'URL devrait être ajoutée avec la clé 'action_url'")

            except Exception as e:
                print(f"    ❌ Erreur lors de la lecture des données: {e}")
        else:
            print(f"    ⚠️ Pas de données JSON")

    # Suggestion de correction
    print("\n" + "=" * 70)
    print("💡 SUGGESTIONS")
    print("=" * 70)

    if terms_notifications:
        latest = terms_notifications[0]
        if not latest.data or 'action_url' not in latest.data:
            print("Pour corriger le problème de redirection:")
            print("\n1. La notification doit avoir 'action_url' dans ses données:")
            print("   notification.data = {'action_url': 'http://localhost:8080/annexes/terms'}")

            print("\n2. Le JavaScript vérifie maintenant:")
            print("   - data.action_url (priorité)")
            print("   - Fallback sur localhost:8080 si terms/conditions dans le message")

            print("\n3. Pour corriger les notifications existantes, utilisez:")
            print("   python apps/notification/tests/fix_notification_urls.py")

    return True

if __name__ == "__main__":
    print("🚀 Open Linguify - Vérification des données de notification")
    print("=" * 70)

    success = check_notification_data()

    if success:
        print("\n✅ Vérification terminée")
    else:
        print("\n⚠️ Vérification échouée")
        sys.exit(1)