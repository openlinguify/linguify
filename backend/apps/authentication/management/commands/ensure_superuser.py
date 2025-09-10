"""
Commande Django pour créer automatiquement un superuser
à partir des variables d'environnement si il n'existe pas déjà.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Crée un superuser automatiquement si les variables DJANGO_SUPERUSER_* sont définies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la création même si un superuser existe déjà',
        )

    def handle(self, *args, **options):
        # Récupérer les variables d'environnement
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(
                self.style.WARNING(
                    'Variables DJANGO_SUPERUSER_* non définies. '
                    'Superuser non créé automatiquement.'
                )
            )
            return

        # Vérifier si un superuser existe déjà
        if User.objects.filter(is_superuser=True).exists() and not options['force']:
            self.stdout.write(
                self.style.SUCCESS('Un superuser existe déjà.')
            )
            return

        # Vérifier si l'utilisateur avec cet email existe déjà
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if not user.is_superuser:
                # Promouvoir l'utilisateur existant en superuser
                user.is_superuser = True
                user.is_staff = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Utilisateur {email} promu en superuser avec succès!'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Superuser {email} existe déjà.')
                )
            return

        # Créer le superuser
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superuser créé avec succès!\n'
                    f'Username: {username}\n'
                    f'Email: {email}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Erreur lors de la création du superuser: {str(e)}'
                )
            )