import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.course.models import ContentLesson, Lesson

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fixes orphaned content lessons by assigning them to lessons'

    def add_arguments(self, parser):
        parser.add_argument(
            '--content_lesson_id',
            type=int,
            help='Fix a specific content lesson ID'
        )
        parser.add_argument(
            '--target_lesson_id',
            type=int,
            help='Assign orphaned content lessons to this specific lesson ID'
        )
        parser.add_argument(
            '--list-only',
            action='store_true',
            help='Only list orphaned content lessons without fixing them'
        )

    def handle(self, *args, **options):
        content_lesson_id = options.get('content_lesson_id')
        target_lesson_id = options.get('target_lesson_id')
        list_only = options.get('list_only')

        # Get orphaned content lessons
        orphaned_query = ContentLesson.objects.filter(lesson__isnull=True)
        
        if content_lesson_id:
            orphaned_query = orphaned_query.filter(id=content_lesson_id)
        
        orphaned_content_lessons = list(orphaned_query)
        
        if not orphaned_content_lessons:
            self.stdout.write(self.style.SUCCESS('No orphaned content lessons found'))
            return
        
        # Display orphaned content lessons
        self.stdout.write(f'Found {len(orphaned_content_lessons)} orphaned content lessons:')
        for cl in orphaned_content_lessons:
            self.stdout.write(f'  ID: {cl.id}, Type: {cl.content_type}, Title: {cl.title_en}')
        
        if list_only:
            return
        
        # Determine target lesson
        target_lesson = None
        if target_lesson_id:
            try:
                target_lesson = Lesson.objects.get(id=target_lesson_id)
                self.stdout.write(f'Using specified lesson: {target_lesson.id} - {target_lesson.title_en}')
            except Lesson.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Lesson with ID {target_lesson_id} not found'))
                return
        else:
            # Find a suitable lesson (first lesson in the database)
            target_lesson = Lesson.objects.order_by('id').first()
            if not target_lesson:
                self.stdout.write(self.style.ERROR('No lessons available to use as target'))
                return
            self.stdout.write(f'Using first available lesson: {target_lesson.id} - {target_lesson.title_en}')
        
        # Fix orphaned content lessons
        fixed_count = 0
        
        with transaction.atomic():
            for content_lesson in orphaned_content_lessons:
                content_lesson.lesson = target_lesson
                content_lesson.save(update_fields=['lesson'])
                fixed_count += 1
                self.stdout.write(f'Fixed content lesson {content_lesson.id} - Now assigned to lesson {target_lesson.id}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully fixed {fixed_count} orphaned content lessons'))