#!/usr/bin/env python
"""
Script pour envoyer des notifications de test dans toutes les langues
"""
import os
import sys
import django
from datetime import datetime

# Remonter au répertoire backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.notification.services import NotificationService, NotificationDeliveryService
from apps.notification.models import Notification, NotificationType, NotificationPriority

User = get_user_model()

def send_test_notifications():
    """Envoie des notifications de test dans toutes les langues"""

    # Utiliser l'utilisateur linguify.info@gmail.com
    try:
        user = User.objects.get(email='linguify.info@gmail.com')
        print(f"✓ Utilisateur trouvé : {user.username} ({user.email})")
        original_language = user.interface_language
    except User.DoesNotExist:
        # Créer l'utilisateur s'il n'existe pas
        print("⚠️ Utilisateur linguify.info@gmail.com non trouvé, création...")
        user = User.objects.create_user(
            username='linguify_test',
            email='linguify.info@gmail.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='Linguify',
            interface_language='en'
        )
        print(f"✓ Utilisateur créé : {user.username}")
        original_language = 'en'

    languages = [
        ('en', 'English', '🇬🇧'),
        ('fr', 'Français', '🇫🇷'),
        ('nl', 'Nederlands', '🇳🇱'),
        ('es', 'Español', '🇪🇸')
    ]

    print("\n" + "=" * 70)
    print("🔔 ENVOI DES NOTIFICATIONS DANS TOUTES LES LANGUES")
    print("=" * 70)
    print(f"Utilisateur: {user.email}")
    print(f"Date/Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    notifications_created = []

    for lang_code, lang_name, flag in languages:
        print(f"\n{flag} Notifications en {lang_name} ({lang_code.upper()})")
        print("-" * 50)

        # Changer la langue de l'utilisateur
        user.interface_language = lang_code
        user.save()

        # 1. Notification de révision (flashcards)
        try:
            notif = NotificationService.notify_flashcard_review(user, 25)
            if notif:
                notifications_created.append(notif)
                print(f"  ✅ Révision: {notif.title}")
                print(f"     Message: {notif.message}")
        except Exception as e:
            print(f"  ❌ Erreur révision: {str(e)}")

        # 2. Notification d'achievement
        try:
            achievement = {
                'en': '100 words learned!',
                'fr': '100 mots appris !',
                'nl': '100 woorden geleerd!',
                'es': '¡100 palabras aprendidas!'
            }[lang_code]

            notif = NotificationService.notify_achievement_unlocked(user, achievement)
            if notif:
                notifications_created.append(notif)
                print(f"  ✅ Achievement: {notif.title}")
                print(f"     Message: {notif.message}")
        except Exception as e:
            print(f"  ❌ Erreur achievement: {str(e)}")

        # 3. Notification de cours terminé
        try:
            course = {
                'en': 'French A1',
                'fr': 'Français A1',
                'nl': 'Frans A1',
                'es': 'Francés A1'
            }[lang_code]

            notif = NotificationService.notify_course_completed(user, course)
            if notif:
                notifications_created.append(notif)
                print(f"  ✅ Cours terminé: {notif.title}")
                print(f"     Message: {notif.message}")
        except Exception as e:
            print(f"  ❌ Erreur cours: {str(e)}")

        # 4. Notification système
        try:
            update = {
                'en': 'New features available! Check out the improved flashcard system.',
                'fr': 'Nouvelles fonctionnalités disponibles ! Découvrez le système de cartes amélioré.',
                'nl': 'Nieuwe functies beschikbaar! Bekijk het verbeterde flashcard-systeem.',
                'es': '¡Nuevas funciones disponibles! Descubre el sistema de tarjetas mejorado.'
            }[lang_code]

            notif = NotificationService.notify_system_update(user, update)
            if notif:
                notifications_created.append(notif)
                print(f"  ✅ Système: {notif.title}")
                print(f"     Message: {notif.message}")
        except Exception as e:
            print(f"  ❌ Erreur système: {str(e)}")

        # 5. Notification personnalisée avec priorité haute
        try:
            if lang_code == 'en':
                title = "🎯 Daily Goal Achieved!"
                message = "Congratulations! You've completed your daily learning goal."
            elif lang_code == 'fr':
                title = "🎯 Objectif quotidien atteint !"
                message = "Félicitations ! Vous avez atteint votre objectif d'apprentissage quotidien."
            elif lang_code == 'nl':
                title = "🎯 Dagelijks doel bereikt!"
                message = "Gefeliciteerd! Je hebt je dagelijkse leerdoel bereikt."
            else:  # es
                title = "🎯 ¡Objetivo diario alcanzado!"
                message = "¡Felicidades! Has completado tu objetivo de aprendizaje diario."

            notif = NotificationDeliveryService.create_and_deliver(
                user=user,
                title=title,
                message=message,
                notification_type=NotificationType.ACHIEVEMENT,
                priority=NotificationPriority.HIGH,
                data={'type': 'daily_goal', 'language': lang_code}
            )
            if notif:
                notifications_created.append(notif)
                print(f"  ✅ Objectif quotidien: {notif.title}")
        except Exception as e:
            print(f"  ❌ Erreur objectif: {str(e)}")

    # Restaurer la langue originale
    user.interface_language = original_language
    user.save()
    print(f"\n🔄 Langue utilisateur restaurée: {original_language}")

    # Afficher les notifications créées
    print("\n" + "=" * 70)
    print("📋 NOTIFICATIONS CRÉÉES")
    print("=" * 70)
    print(f"Total: {len(notifications_created)} notifications")

    # Grouper par langue approximative
    by_priority = {}
    for notif in notifications_created:
        priority = notif.priority
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append(notif)

    for priority in ['high', 'medium', 'low']:
        if priority in by_priority:
            print(f"\n{priority.upper()} Priority ({len(by_priority[priority])} notifications):")
            for notif in by_priority[priority][:5]:  # Limiter l'affichage
                status = "🔵" if not notif.is_read else "⚪"
                print(f"  {status} {notif.title[:50]}")

    # Instructions pour voir les notifications
    print("\n" + "=" * 70)
    print("📱 POUR VOIR LES NOTIFICATIONS")
    print("=" * 70)
    print("1. Connectez-vous à l'application avec:")
    print(f"   Email: {user.email}")
    print(f"   Mot de passe: TestPassword123!")
    print("\n2. Les notifications apparaîtront dans:")
    print("   • L'icône cloche dans le header")
    print("   • Le centre de notifications")
    print("   • En temps réel via WebSocket")
    print("\n3. Les notifications sont traduites selon interface_language")

    return len(notifications_created)

if __name__ == "__main__":
    print("🚀 Open Linguify - Test Notifications Multilingues")
    print("=" * 70)

    count = send_test_notifications()

    if count > 0:
        print(f"\n✨ {count} notifications créées avec succès!")
        print("📧 Connectez-vous avec linguify.info@gmail.com pour les voir")
    else:
        print("\n⚠️ Aucune notification n'a pu être créée")
        sys.exit(1)