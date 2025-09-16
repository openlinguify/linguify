# backend/core/subscription/management/commands/setup_subscription_plans.py
from django.core.management.base import BaseCommand
from core.subscription.models import create_default_plans


class Command(BaseCommand):
    help = 'Crée les plans d\'abonnement par défaut'

    def handle(self, *args, **options):
        self.stdout.write("Création des plans d'abonnement par défaut...")
        create_default_plans()
        self.stdout.write(
            self.style.SUCCESS('Plans d\'abonnement créés avec succès!')
        )