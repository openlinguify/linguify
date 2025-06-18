from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Test command to verify core app management commands work'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Core management commands are working!'))