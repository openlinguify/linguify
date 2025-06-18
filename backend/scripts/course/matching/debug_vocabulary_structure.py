from django.core.management.base import BaseCommand
from apps.course.models import Lesson, ContentLesson, VocabularyList

class Command(BaseCommand):
    help = "Debug vocabulary structure in lessons"
    
    def handle(self, *args, **options):
        # Check a few lessons to understand structure
        lessons = Lesson.objects.all()[:5]  # Check first 5 lessons
        
        for lesson in lessons:
            self.stdout.write(f"\nLesson: {lesson.title_en} (ID: {lesson.id})")
            
            # Check all content lessons
            content_lessons = ContentLesson.objects.filter(lesson=lesson)
            self.stdout.write(f"  Total content lessons: {content_lessons.count()}")
            
            # Check vocabulary content
            vocab_contents = content_lessons.filter(content_type='vocabulary')
            self.stdout.write(f"  Vocabulary content lessons: {vocab_contents.count()}")
            
            for content in vocab_contents:
                self.stdout.write(f"    Content: {content.title_en or content.title_fr}")
                
                # Check for VocabularyList
                vocab_lists = VocabularyList.objects.filter(content_lesson=content)
                self.stdout.write(f"      Vocabulary lists: {vocab_lists.count()}")
                
                for vocab_list in vocab_lists:
                    item_count = vocab_list.vocabularyitem_set.count()
                    self.stdout.write(f"        List {vocab_list.id}: {item_count} items")
                    
                    # Show first 3 items
                    items = vocab_list.vocabularyitem_set.all()[:3]
                    for item in items:
                        self.stdout.write(f"          - {item.original_word} / {item.translated_word_en}")
            
            # Check matching content
            matching_contents = content_lessons.filter(content_type='matching')
            self.stdout.write(f"  Matching content lessons: {matching_contents.count()}")