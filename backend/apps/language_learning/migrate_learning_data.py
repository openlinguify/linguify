#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de migration pour transférer les données d'apprentissage
depuis le modèle User vers UserLearningProfile.

Usage:
    python manage.py shell < apps/language_learning/migrations/migrate_learning_data.py
    ou
    python manage.py runscript migrate_learning_data
"""

from django.contrib.auth import get_user_model
from apps.language_learning.models import UserLearningProfile
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def migrate_learning_profiles():
    """
    Migre les données d'apprentissage des langues depuis User vers UserLearningProfile
    """
    users = User.objects.all()
    created_count = 0
    updated_count = 0
    error_count = 0

    print(f"Migration de {users.count()} utilisateurs...")

    for user in users:
        try:
            # Vérifier si le profil existe déjà
            profile, created = UserLearningProfile.objects.get_or_create(
                user=user,
                defaults={
                    'native_language': getattr(user, 'native_language', 'EN'),
                    'target_language': getattr(user, 'target_language', 'FR'),
                    'language_level': getattr(user, 'language_level', 'A1'),
                    'objectives': getattr(user, 'objectives', 'Personal'),
                    'speaking_exercises': getattr(user, 'speaking_exercises', True),
                    'listening_exercises': getattr(user, 'listening_exercises', True),
                    'reading_exercises': getattr(user, 'reading_exercises', True),
                    'writing_exercises': getattr(user, 'writing_exercises', True),
                    'daily_goal': getattr(user, 'daily_goal', 15),
                    'weekday_reminders': getattr(user, 'weekday_reminders', True),
                    'weekend_reminders': getattr(user, 'weekend_reminders', False),
                    'reminder_time': getattr(user, 'reminder_time', '18:00'),
                }
            )

            if created:
                created_count += 1
                logger.info(f"✅ Profil créé pour {user.username}")
            else:
                # Mettre à jour le profil existant si nécessaire
                updated_fields = []

                # Vérifier et mettre à jour chaque champ
                fields_to_check = [
                    'native_language', 'target_language', 'language_level', 'objectives',
                    'speaking_exercises', 'listening_exercises', 'reading_exercises',
                    'writing_exercises', 'daily_goal', 'weekday_reminders',
                    'weekend_reminders', 'reminder_time'
                ]

                for field in fields_to_check:
                    user_value = getattr(user, field, None)
                    if user_value is not None and getattr(profile, field) != user_value:
                        setattr(profile, field, user_value)
                        updated_fields.append(field)

                if updated_fields:
                    profile.save()
                    updated_count += 1
                    logger.info(f"✏️ Profil mis à jour pour {user.username}: {', '.join(updated_fields)}")

        except Exception as e:
            error_count += 1
            logger.error(f"❌ Erreur pour {user.username}: {str(e)}")

    print(f"\n📊 Résumé de la migration:")
    print(f"   - Profils créés: {created_count}")
    print(f"   - Profils mis à jour: {updated_count}")
    print(f"   - Erreurs: {error_count}")
    print(f"   - Total traité: {users.count()}")

    return {
        'created': created_count,
        'updated': updated_count,
        'errors': error_count,
        'total': users.count()
    }


def verify_migration():
    """
    Vérifie que la migration s'est bien effectuée
    """
    users_with_learning_data = User.objects.exclude(
        native_language__isnull=True,
        target_language__isnull=True
    ).count()

    profiles_count = UserLearningProfile.objects.count()

    print(f"\n🔍 Vérification de la migration:")
    print(f"   - Utilisateurs avec données d'apprentissage: {users_with_learning_data}")
    print(f"   - Profils d'apprentissage créés: {profiles_count}")

    if users_with_learning_data == profiles_count:
        print("   ✅ Migration complète!")
    else:
        print(f"   ⚠️ Différence détectée: {users_with_learning_data - profiles_count} profils manquants")


def rollback_migration():
    """
    Annule la migration (supprime tous les UserLearningProfile)
    À utiliser avec précaution!
    """
    count = UserLearningProfile.objects.count()

    confirm = input(f"⚠️ Êtes-vous sûr de vouloir supprimer {count} profils? (yes/no): ")

    if confirm.lower() == 'yes':
        UserLearningProfile.objects.all().delete()
        print(f"✅ {count} profils supprimés")
    else:
        print("❌ Annulation...")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        rollback_migration()
    elif len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_migration()
    else:
        migrate_learning_profiles()
        verify_migration()