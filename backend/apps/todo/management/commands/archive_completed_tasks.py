from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from datetime import timedelta
import json

from apps.todo.models.todo_models import Task, PersonalStageType

User = get_user_model()


class Command(BaseCommand):
    help = 'Archive completed tasks automatically based on user settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be archived without actually doing it',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Process only specific user ID',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        user_id = options.get('user_id')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Get users to process
        users = User.objects.all()
        if user_id:
            users = users.filter(id=user_id)
            
        total_archived = 0
        users_processed = 0
        
        for user in users:
            self.stdout.write(f'Processing user: {user.username}')
            archived_count = self.process_user(user, dry_run)
            if archived_count > 0:
                total_archived += archived_count
                users_processed += 1
                self.stdout.write(
                    f'User {user.username}: {archived_count} tasks archived'
                )
            else:
                self.stdout.write(f'User {user.username}: No tasks to archive')
        
        if total_archived > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully processed {users_processed} users, '
                    f'{total_archived} tasks archived'
                )
            )
        else:
            self.stdout.write('No tasks to archive')

    def process_user(self, user, dry_run=False):
        """Process auto-archiving for a specific user"""
        
        # Get user settings from cache
        cache_key = f"todo_settings_{user.id}"
        settings_data = cache.get(cache_key)
        
        self.stdout.write(f'  Cache key: {cache_key}')
        self.stdout.write(f'  Settings found: {settings_data}')
        
        if not settings_data:
            # Use default settings for testing/fallback
            settings_data = {
                'auto_archive_completed': True,  # Default enabled for this command
                'auto_archive_days': 30
            }
            self.stdout.write(f'  Using default settings for user {user.username}')
            
        # Check if auto-archiving is enabled
        auto_archive_enabled = settings_data.get('auto_archive_completed', False)
        if not auto_archive_enabled:
            self.stdout.write(f'  Auto-archive disabled for user {user.username}')
            return 0
            
        # Get archive days setting
        archive_days = settings_data.get('auto_archive_days', 30)
        cutoff_date = timezone.now() - timedelta(days=archive_days)
        
        # Find Archives stage for this user
        try:
            archives_stage = PersonalStageType.objects.get(
                user=user, 
                name__iexact='Archives'
            )
        except PersonalStageType.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f'User {user.username} has no Archives stage, skipping'
                )
            )
            return 0
        
        # Find completed tasks that should be archived
        # Use completed_at if available, otherwise use updated_at for older tasks
        from django.db.models import Q
        
        tasks_to_archive = Task.objects.filter(
            user=user,
            state='1_done',
            active=True
        ).filter(
            Q(completed_at__lt=cutoff_date) |  # Tasks with completed_at set
            Q(completed_at__isnull=True, updated_at__lt=cutoff_date)  # Old tasks without completed_at
        ).exclude(
            personal_stage_type=archives_stage  # Don't archive tasks already in Archives
        )
        
        archived_count = tasks_to_archive.count()
        
        # Debug info
        if dry_run:
            self.stdout.write(f'Debug - User: {user.username}')
            self.stdout.write(f'Debug - Auto archive enabled: {auto_archive_enabled}')
            self.stdout.write(f'Debug - Archive days: {archive_days}')
            self.stdout.write(f'Debug - Cutoff date: {cutoff_date}')
            self.stdout.write(f'Debug - Archives stage: {archives_stage.name if archives_stage else "None"}')
            
            # Show all completed tasks
            all_completed = Task.objects.filter(user=user, state='1_done', active=True)
            self.stdout.write(f'Debug - Total completed tasks: {all_completed.count()}')
            
            for task in all_completed:
                stage_name = task.personal_stage_type.name if task.personal_stage_type else "None"
                completed_date = task.completed_at or task.updated_at
                eligible = "YES" if completed_date < cutoff_date and task.personal_stage_type != archives_stage else "NO"
                self.stdout.write(f'  - {task.title} | Stage: {stage_name} | Date: {completed_date} | Eligible: {eligible}')
                
            # Show the actual query that would be executed
            self.stdout.write(f'Debug - Tasks matching query: {tasks_to_archive.count()}')
        
        if not dry_run and archived_count > 0:
            # Move tasks to Archives stage
            tasks_to_archive.update(personal_stage_type=archives_stage)
            
            self.stdout.write(
                f'Archived {archived_count} tasks for user {user.username} '
                f'(completed before {cutoff_date.strftime("%Y-%m-%d")})'
            )
        elif dry_run and archived_count > 0:
            self.stdout.write(
                f'[DRY RUN] Would archive {archived_count} tasks for user {user.username} '
                f'(completed before {cutoff_date.strftime("%Y-%m-%d")})'
            )
            
        return archived_count