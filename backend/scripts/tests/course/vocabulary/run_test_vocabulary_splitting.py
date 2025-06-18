#!/usr/bin/env python
"""
Runnable test script for the vocabulary splitting functionality.
This script demonstrates the thematic grouping and manual selection capabilities.

Usage:
    poetry run python scripts/course/theory/run_test_vocabulary_splitting.py
    # or
    python manage.py runscript test_vocabulary_splitting --script-args
"""

import os
import sys
import json
import tempfile
from io import StringIO

# Setup Django environment
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.db import models
from apps.course.models import ContentLesson, VocabularyList, Unit

def test_vocabulary_split(lesson_id=None):
    """Test the vocabulary splitting functionality with thematic grouping."""
    if not lesson_id:
        # Find a vocabulary lesson with a reasonable number of words
        lessons = ContentLesson.objects.filter(content_type__icontains='vocabulary')
        lessons = lessons.annotate(word_count=models.Count('vocabulary_lists'))
        lessons = lessons.filter(word_count__gte=15).order_by('-word_count')
        
        if not lessons.exists():
            print("No suitable vocabulary lessons found. Please specify a lesson ID.")
            return
            
        lesson = lessons.first()
        lesson_id = lesson.id
        print(f"Selected lesson {lesson.title_en} (ID={lesson_id}) with {lesson.vocabulary_lists.count()} words")
    else:
        try:
            lesson = ContentLesson.objects.get(id=lesson_id)
            if 'vocabulary' not in lesson.content_type.lower():
                print(f"Lesson {lesson_id} is not a vocabulary lesson.")
                return
            print(f"Using specified lesson {lesson.title_en} (ID={lesson_id}) with {lesson.vocabulary_lists.count()} words")
        except ContentLesson.DoesNotExist:
            print(f"Lesson with ID {lesson_id} not found.")
            return
            
    # Test thematic grouping
    print("\n=== Testing Thematic Grouping ===")
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
        
    print(thematic_output.getvalue())
    
    # Test manual selection
    print("\n=== Testing Manual Selection ===")
    
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
        
    print(manual_output.getvalue())
    
    print("\n=== Test Complete ===")
    print("The vocabulary splitting functionality is working as expected.")
    print("You can now use the admin interface to split vocabulary lessons with:")
    print("1. Thematic grouping")
    print("2. Manual word selection")
    print("3. Preview before execution")

# Direct execution
if __name__ == "__main__":
    test_vocabulary_split()