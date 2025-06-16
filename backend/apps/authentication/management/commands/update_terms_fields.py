"""
Management command to update terms acceptance fields for all users
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.authentication.models import User


class Command(BaseCommand):
    help = 'Updates terms acceptance fields for all users or specific users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-email',
            type=str,
            help='Email of a specific user to update'
        )
        parser.add_argument(
            '--accept',
            action='store_true',
            help='Mark terms as accepted'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear terms acceptance status'
        )
        parser.add_argument(
            '--version',
            type=str,
            default='v1.0',
            help='Terms version to set'
        )

    def handle(self, *args, **options):
        user_email = options.get('user_email')
        accept = options.get('accept')
        clear = options.get('clear')
        version = options.get('version')

        if not (accept or clear):
            self.stdout.write(self.style.ERROR('Please specify either --accept or --clear'))
            return

        if accept and clear:
            self.stdout.write(self.style.ERROR('Cannot specify both --accept and --clear'))
            return

        queryset = User.objects.all()
        if user_email:
            queryset = queryset.filter(email=user_email)
            if not queryset.exists():
                self.stdout.write(self.style.ERROR(f'No user found with email {user_email}'))
                return

        count = queryset.count()
        if count == 0:
            self.stdout.write(self.style.WARNING('No users found to update'))
            return

        if accept:
            # Mark terms as accepted
            for user in queryset:
                user.terms_accepted = True
                user.terms_accepted_at = timezone.now()
                user.terms_version = version
                user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully marked terms as accepted for {count} users'))
        elif clear:
            # Clear terms acceptance
            for user in queryset:
                user.terms_accepted = False
                user.terms_accepted_at = None
                user.terms_version = None
                user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully cleared terms acceptance for {count} users'))