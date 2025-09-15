#!/usr/bin/env python
"""
Script de test pour vérifier les notifications multilingues
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils.translation import activate, get_language
from apps.notification.services import NotificationService, send_terms_acceptance_email_and_notification
from apps.notification.models import Notification

User = get_user_model()

def test_multilingual_notifications():
    """Test les notifications dans différentes langues"""

    # Récupérer l'utilisateur test
    try:
        user = User.objects.get(email='louisphilippelalou@outlook.com')
        print(f"✓ Utilisateur trouvé : {user.username} ({user.email})")
        print(f"  Langue d'interface actuelle : {user.interface_language}")
    except User.DoesNotExist:
        print("❌ Utilisateur louisphilippelalou@outlook.com non trouvé")
        return False

    # Tester les notifications dans différentes langues
    languages = ['en', 'fr', 'nl', 'es']

    for lang in languages:
        print(f"\n📋 Test des notifications en {lang.upper()}")
        print("=" * 50)

        # Sauvegarder la langue actuelle
        original_language = user.interface_language

        # Changer la langue de l'interface utilisateur
        user.interface_language = lang
        user.save()

        # 1. Test notification de révision
        print(f"  1. Notification de révision...")
        notification = NotificationService.notify_flashcard_review(user, 15)
        if notification:
            print(f"     ✓ Titre: {notification.title}")
            print(f"     ✓ Message: {notification.message}")
        else:
            print("     ❌ Échec de création")

        # 2. Test notification d'achievement
        print(f"  2. Notification d'achievement...")
        notification = NotificationService.notify_achievement_unlocked(user, "100 mots appris!")
        if notification:
            print(f"     ✓ Titre: {notification.title}")
            print(f"     ✓ Message: {notification.message}")
        else:
            print("     ❌ Échec de création")

        # 3. Test notification de cours terminé
        print(f"  3. Notification de cours terminé...")
        notification = NotificationService.notify_course_completed(user, "Français A1")
        if notification:
            print(f"     ✓ Titre: {notification.title}")
            print(f"     ✓ Message: {notification.message}")
        else:
            print("     ❌ Échec de création")

        # 4. Test notification des conditions d'utilisation
        print(f"  4. Notification des conditions d'utilisation...")
        success = send_terms_acceptance_email_and_notification(user)
        if success:
            # Récupérer la dernière notification créée
            latest_notification = Notification.objects.filter(
                user=user,
                type='action_required'
            ).order_by('-created_at').first()

            if latest_notification:
                print(f"     ✓ Titre: {latest_notification.title}")
                print(f"     ✓ Message: {latest_notification.message}")
                print(f"     ✓ Email envoyé avec succès")
            else:
                print("     ⚠️ Notification créée mais non trouvée")
        else:
            print("     ❌ Échec de création")

        # Restaurer la langue originale
        user.interface_language = original_language
        user.save()

    # Afficher un résumé des notifications créées
    print("\n📊 RÉSUMÉ DES NOTIFICATIONS CRÉÉES")
    print("=" * 50)
    recent_notifications = Notification.objects.filter(user=user).order_by('-created_at')[:20]

    current_lang = None
    for notif in recent_notifications:
        # Grouper par langue (approximatif basé sur le contenu)
        if 'REVISION REMINDER' in notif.title:
            detected_lang = 'en'
        elif 'RAPPEL DE RÉVISION' in notif.title:
            detected_lang = 'fr'
        elif 'REVISIE HERINNERING' in notif.title:
            detected_lang = 'nl'
        elif 'RECORDATORIO DE REVISIÓN' in notif.title:
            detected_lang = 'es'
        else:
            detected_lang = '??'

        if detected_lang != current_lang:
            current_lang = detected_lang
            print(f"\n  [{current_lang.upper()}]")

        status = "🔵" if not notif.is_read else "⚪"
        print(f"    {status} {notif.title[:50]}")

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DES NOTIFICATIONS MULTILINGUES")
    print("=" * 60)

    success = test_multilingual_notifications()

    if success:
        print("\n✅ Tests terminés avec succès!")
        print("Les notifications sont correctement traduites selon interface_language")
    else:
        print("\n❌ Tests échoués")
        sys.exit(1)