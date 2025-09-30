"""
Commande de gestion pour initialiser les langues de base dans le système
"""
from django.core.management.base import BaseCommand
from apps.language_learning.models import Language


class Command(BaseCommand):
    help = 'Initialise les langues de base dans le système'

    def handle(self, *args, **options):
        languages_data = [
            {
                'code': 'EN',
                'name': 'English',
                'native_name': 'English',
                'flag_emoji': '🇬🇧',
                'is_active': True
            },
            {
                'code': 'FR',
                'name': 'French',
                'native_name': 'Français',
                'flag_emoji': '🇫🇷',
                'is_active': True
            },
            {
                'code': 'ES',
                'name': 'Spanish',
                'native_name': 'Español',
                'flag_emoji': '🇪🇸',
                'is_active': True
            },
            {
                'code': 'DE',
                'name': 'German',
                'native_name': 'Deutsch',
                'flag_emoji': '🇩🇪',
                'is_active': True
            },
            {
                'code': 'IT',
                'name': 'Italian',
                'native_name': 'Italiano',
                'flag_emoji': '🇮🇹',
                'is_active': True
            },
            {
                'code': 'NL',
                'name': 'Dutch',
                'native_name': 'Nederlands',
                'flag_emoji': '🇳🇱',
                'is_active': True
            }
        ]

        created_count = 0
        updated_count = 0

        for lang_data in languages_data:
            language, created = Language.objects.get_or_create(
                code=lang_data['code'],
                defaults=lang_data
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Langue créée: {language.name} ({language.code})')
                )
            else:
                # Mettre à jour les données si la langue existe déjà
                for field, value in lang_data.items():
                    setattr(language, field, value)
                language.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Langue mise à jour: {language.name} ({language.code})')
                )

        self.stdout.write(
            self.style.SUCCESS(f'🎉 Terminé! {created_count} langues créées, {updated_count} mises à jour.')
        )