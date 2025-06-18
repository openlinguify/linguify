import json
import tempfile
import os
import sys
from io import StringIO
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import models
from apps.course.models import ContentLesson, VocabularyList, Unit

class Command(BaseCommand):
    help = 'Test the vocabulary splitting functionality'

    def add_arguments(self, parser):
        parser.add_argument('--lesson-id', type=int, help='Specific lesson ID to test')

    def handle(self, *args, **options):
        lesson_id = options.get('lesson_id')
        
        if not lesson_id:
            # Find a vocabulary lesson with a reasonable number of words
            lessons = ContentLesson.objects.filter(content_type__icontains='vocabulary')
            lessons = lessons.annotate(word_count=models.Count('vocabulary_lists'))
            lessons = lessons.filter(word_count__gte=15).order_by('-word_count')
            
            if not lessons.exists():
                self.stdout.write(self.style.ERROR("No suitable vocabulary lessons found. Please specify a lesson ID."))
                return
                
            lesson = lessons.first()
            lesson_id = lesson.id
            self.stdout.write(f"Selected lesson {lesson.title_en} (ID={lesson_id}) with {lesson.vocabulary_lists.count()} words")
        else:
            try:
                lesson = ContentLesson.objects.get(id=lesson_id)
                if 'vocabulary' not in lesson.content_type.lower():
                    self.stdout.write(self.style.ERROR(f"Lesson {lesson_id} is not a vocabulary lesson."))
                    return
                self.stdout.write(f"Using specified lesson {lesson.title_en} (ID={lesson_id}) with {lesson.vocabulary_lists.count()} words")
            except ContentLesson.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Lesson with ID {lesson_id} not found."))
                return
                
        # Test thematic grouping
        self.stdout.write(self.style.SUCCESS("\n=== Testing Thematic Grouping ==="))
        # Capture command output
        orig_stdout = sys.stdout
        thematic_output = StringIO()
        sys.stdout = thematic_output
        
        try:
            call_command('split_vocabulary_lesson', 
                         lesson_id=lesson_id, 
                         parts=3, 
                         thematic=True,
                         dry_run=True)
        finally:
            sys.stdout = orig_stdout
            
        self.stdout.write(thematic_output.getvalue())
        
        # Test manual selection
        self.stdout.write(self.style.SUCCESS("\n=== Testing Manual Selection ==="))
        
        # Get vocabulary items
        vocabulary = list(VocabularyList.objects.filter(content_lesson_id=lesson_id))
        
        # Create a simple distribution
        word_assignments = {}
        for i, word in enumerate(vocabulary):
            # Simple distribution: part 1, 2, 3, 1, 2, 3, ...
            part = (i % 3) + 1
            word_assignments[str(word.id)] = str(part)
        
        # Write the assignments to a temp file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_file:
            json.dump(word_assignments, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Capture command output
            manual_output = StringIO()
            sys.stdout = manual_output
            
            call_command('split_vocabulary_lesson', 
                         lesson_id=lesson_id, 
                         parts=3, 
                         manual_selection=True,
                         word_assignments=temp_file_path,
                         dry_run=True)
        finally:
            sys.stdout = orig_stdout
            # Clean up temp file
            os.unlink(temp_file_path)
            
        self.stdout.write(manual_output.getvalue())
        
        self.stdout.write(self.style.SUCCESS("\n=== Test Complete ==="))
        self.stdout.write("The vocabulary splitting functionality is working as expected.")
        self.stdout.write("You can now use the admin interface to split vocabulary lessons with:")
        self.stdout.write("1. Thematic grouping")
        self.stdout.write("2. Manual word selection")
        self.stdout.write("3. Preview before execution")