"""
Commande Django pour promouvoir un utilisateur existant en superuser.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Promeut un utilisateur existant en superuser'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email de l\'utilisateur à promouvoir en superuser'
        )

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            user = User.objects.get(email=email)
            
            if user.is_superuser:
                self.stdout.write(
                    self.style.WARNING(f'L\'utilisateur {email} est déjà superuser.')
                )
                return
                
            user.is_superuser = True
            user.is_staff = True
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Utilisateur {email} promu en superuser avec succès!'
                )
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Utilisateur avec l\'email {email} n\'existe pas.')
            )