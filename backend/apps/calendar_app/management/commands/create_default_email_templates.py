"""
Management command to create default email templates
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.calendar_app.models import CalendarEmailTemplate
from apps.calendar_app.services.email_service import EmailTemplateManager

User = get_user_model()


class Command(BaseCommand):
    help = 'Create default email templates for calendar notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username of the user to assign templates to (defaults to first superuser)',
        )
        parser.add_argument(
            '--language',
            type=str,
            default='en',
            help='Language code for templates (default: en)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of existing templates',
        )

    def handle(self, *args, **options):
        # Get user for template creation
        username = options.get('user')
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{username}" not found')
                )
                return
        else:
            # Get first superuser
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(
                    self.style.ERROR('No superuser found. Please create one first.')
                )
                return

        language = options.get('language', 'en')
        force = options.get('force', False)

        self.stdout.write(f'Creating email templates for user: {user.username}')
        self.stdout.write(f'Language: {language}')

        # Check if templates already exist
        existing_count = CalendarEmailTemplate.objects.filter(
            language=language,
            is_default=True
        ).count()

        if existing_count > 0 and not force:
            self.stdout.write(
                self.style.WARNING(
                    f'Found {existing_count} existing default templates for language "{language}". '
                    'Use --force to recreate them.'
                )
            )
            return

        if force and existing_count > 0:
            # Delete existing default templates
            deleted_count = CalendarEmailTemplate.objects.filter(
                language=language,
                is_default=True
            ).delete()[0]
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing templates')
            )

        # Create templates
        try:
            templates = EmailTemplateManager.create_default_templates(user)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {len(templates)} email templates:'
                )
            )
            
            for template in templates:
                self.stdout.write(f'  ✓ {template.get_template_type_display()} ({template.language})')

            # Show template context help
            self.stdout.write('\n' + self.style.HTTP_INFO('Available template variables:'))
            context_vars = EmailTemplateManager.get_template_context_variables()
            
            for category, variables in context_vars.items():
                self.stdout.write(f'\n{category.upper()}:')
                for var, description in variables.items():
                    self.stdout.write(f'  {{ {category}.{var} }} - {description}')

            self.stdout.write(
                self.style.HTTP_INFO(
                    '\nYou can now customize these templates in the Django admin interface.'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating templates: {str(e)}')
            )
            raise