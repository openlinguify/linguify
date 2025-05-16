import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.course.models import ContentLesson, Lesson, TestRecap

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fixes content lesson 58 and ensures it has a parent lesson and TestRecap'

    def add_arguments(self, parser):
        parser.add_argument(
            '--target_lesson_id',
            type=int,
            help='Assign content lesson 58 to this specific lesson ID'
        )

    def handle(self, *args, **options):
        target_lesson_id = options.get('target_lesson_id')
        
        # Get content lesson 58
        try:
            content_lesson = ContentLesson.objects.get(id=58)
            self.stdout.write(f'Found content lesson 58: {content_lesson.title_en}, type: {content_lesson.content_type}')
            
            # Check if content lesson already has a parent
            if content_lesson.lesson:
                self.stdout.write(f'Content lesson 58 has parent lesson: {content_lesson.lesson.id} - {content_lesson.lesson.title_en}')
                parent_lesson = content_lesson.lesson
            else:
                self.stdout.write('Content lesson 58 has no parent lesson')
                
                # Determine target lesson
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
                
                # Fix the content lesson
                with transaction.atomic():
                    content_lesson.lesson = target_lesson
                    content_lesson.save(update_fields=['lesson'])
                    self.stdout.write(f'Fixed content lesson 58 - Now assigned to lesson {target_lesson.id}')
                    parent_lesson = target_lesson
            
            # Check if the parent lesson has a TestRecap
            test_recap = TestRecap.objects.filter(lesson=parent_lesson).first()
            if test_recap:
                self.stdout.write(f'Parent lesson has TestRecap: {test_recap.id} - {test_recap.title}')
            else:
                self.stdout.write('Parent lesson has no TestRecap, creating one...')
                
                # Create a TestRecap for the parent lesson
                from apps.course.management.commands.create_test_recaps import Command as CreateTestRecapsCommand
                create_cmd = CreateTestRecapsCommand()
                create_cmd.handle(lesson_id=parent_lesson.id, limit=1, force=False)
                
                # Verify TestRecap was created
                test_recap = TestRecap.objects.filter(lesson=parent_lesson).first()
                if test_recap:
                    self.stdout.write(f'Created TestRecap: {test_recap.id} - {test_recap.title}')
                else:
                    self.stdout.write(self.style.ERROR('Failed to create TestRecap'))
            
            self.stdout.write(self.style.SUCCESS('Content lesson 58 fix complete'))
            
        except ContentLesson.DoesNotExist:
            self.stdout.write(self.style.ERROR('Content lesson with ID 58 not found'))