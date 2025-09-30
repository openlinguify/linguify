#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Management command pour migrer les données d'apprentissage
depuis le modèle User vers UserLearningProfile.

Usage:
    python manage.py migrate_user_learning_profiles
    python manage.py migrate_user_learning_profiles --check
    python manage.py migrate_user_learning_profiles --rollback
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.language_learning.models import UserLearningProfile
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Migre les données d\'apprentissage depuis User vers UserLearningProfile'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Vérifie seulement le statut de la migration sans la faire',
        )
        parser.add_argument(
            '--rollback',
            action='store_true',
            help='Annule la migration (supprime tous les UserLearningProfile)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Nombre d\'utilisateurs à traiter par batch (défaut: 100)',
        )

    def handle(self, *args, **options):
        if options['check']:
            self.check_migration_status()
        elif options['rollback']:
            self.rollback_migration()
        else:
            self.migrate_profiles(batch_size=options['batch_size'])

    def check_migration_status(self):
        """Vérifie le statut de la migration"""
        total_users = User.objects.count()
        users_with_data = User.objects.exclude(
            native_language__isnull=True,
            target_language__isnull=True
        ).count()
        existing_profiles = UserLearningProfile.objects.count()

        self.stdout.write(self.style.SUCCESS('📊 Statut de la migration:'))
        self.stdout.write(f'   Total d\'utilisateurs: {total_users}')
        self.stdout.write(f'   Utilisateurs avec données d\'apprentissage: {users_with_data}')
        self.stdout.write(f'   Profils d\'apprentissage existants: {existing_profiles}')

        if users_with_data == existing_profiles:
            self.stdout.write(self.style.SUCCESS('✅ Migration complète!'))
        elif existing_profiles > 0:
            self.stdout.write(self.style.WARNING(f'⚠️  Migration partielle: {users_with_data - existing_profiles} profils manquants'))
        else:
            self.stdout.write(self.style.WARNING('❌ Migration non effectuée'))

    def rollback_migration(self):
        """Annule la migration"""
        count = UserLearningProfile.objects.count()

        if count == 0:
            self.stdout.write(self.style.WARNING('Aucun profil à supprimer'))
            return

        confirm = input(f'⚠️  Êtes-vous sûr de vouloir supprimer {count} profils? (yes/no): ')

        if confirm.lower() == 'yes':
            with transaction.atomic():
                UserLearningProfile.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'✅ {count} profils supprimés'))
        else:
            self.stdout.write('❌ Annulation...')

    def migrate_profiles(self, batch_size=100):
        """Effectue la migration par batch"""
        users = User.objects.all()
        total = users.count()
        created = 0
        updated = 0
        errors = 0

        self.stdout.write(self.style.SUCCESS(f'🚀 Début de la migration de {total} utilisateurs...'))

        # Traitement par batch pour éviter les problèmes de mémoire
        for i in range(0, total, batch_size):
            batch = users[i:i + batch_size]
            self.stdout.write(f'   Traitement du batch {i // batch_size + 1} ({i}-{min(i + batch_size, total)})...')

            with transaction.atomic():
                for user in batch:
                    try:
                        profile, is_created = UserLearningProfile.objects.get_or_create(
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

                        if is_created:
                            created += 1
                            logger.debug(f'✅ Profil créé pour {user.username}')
                        else:
                            # Mettre à jour si nécessaire
                            fields_to_update = []

                            for field in ['native_language', 'target_language', 'language_level',
                                        'objectives', 'speaking_exercises', 'listening_exercises',
                                        'reading_exercises', 'writing_exercises', 'daily_goal',
                                        'weekday_reminders', 'weekend_reminders', 'reminder_time']:
                                user_value = getattr(user, field, None)
                                if user_value is not None and getattr(profile, field) != user_value:
                                    setattr(profile, field, user_value)
                                    fields_to_update.append(field)

                            if fields_to_update:
                                profile.save()
                                updated += 1
                                logger.debug(f'✏️  Profil mis à jour pour {user.username}')

                    except Exception as e:
                        errors += 1
                        logger.error(f'❌ Erreur pour {user.username}: {str(e)}')

        # Résumé final
        self.stdout.write(self.style.SUCCESS('\n📊 Résumé de la migration:'))
        self.stdout.write(self.style.SUCCESS(f'   ✅ Profils créés: {created}'))
        self.stdout.write(self.style.SUCCESS(f'   ✏️  Profils mis à jour: {updated}'))
        if errors > 0:
            self.stdout.write(self.style.ERROR(f'   ❌ Erreurs: {errors}'))
        self.stdout.write(self.style.SUCCESS(f'   📈 Total traité: {total}'))

        # Vérification finale
        self.check_migration_status()

        return {'created': created, 'updated': updated, 'errors': errors, 'total': total}