from django.core.management.base import BaseCommand
from apps.course.models import Lesson, ContentLesson, VocabularyList, VocabularyItem

class Command(BaseCommand):
    help = "Debug vocabulary structure in lessons v2"
    
    def handle(self, *args, **options):
        # Check different ways vocabulary might be linked
        self.stdout.write("\nChecking vocabulary structure...\n")
        
        # 1. Check direct VocabularyList connections
        vocab_lists = VocabularyList.objects.all()[:5]
        self.stdout.write(f"Total VocabularyLists: {VocabularyList.objects.count()}")
        
        for vocab_list in vocab_lists:
            self.stdout.write(f"\nVocabularyList ID: {vocab_list.id}")
            self.stdout.write(f"  Content lesson: {vocab_list.content_lesson}")
            self.stdout.write(f"  Content type: {vocab_list.content_lesson.content_type}")
            self.stdout.write(f"  Lesson: {vocab_list.content_lesson.lesson}")
            self.stdout.write(f"  Items: {vocab_list.vocabularyitem_set.count()}")
        
        # 2. Check lessons with VocabularyItems directly
        lessons_with_vocab = set()
        for vocab_list in VocabularyList.objects.all():
            if vocab_list.content_lesson and vocab_list.content_lesson.lesson:
                lessons_with_vocab.add(vocab_list.content_lesson.lesson)
        
        self.stdout.write(f"\nLessons with vocabulary: {len(lessons_with_vocab)}")
        
        # 3. Check content types in ContentLesson
        content_types = ContentLesson.objects.values_list('content_type', flat=True).distinct()
        self.stdout.write("\nContent types in ContentLesson:")
        for ct in content_types:
            count = ContentLesson.objects.filter(content_type=ct).count()
            self.stdout.write(f"  {ct}: {count}")
        
        # 4. Check a specific lesson with vocabulary
        if lessons_with_vocab:
            lesson = list(lessons_with_vocab)[0]
            self.stdout.write(f"\nDetailed check for: {lesson.title_en} (ID: {lesson.id})")
            
            content_lessons = ContentLesson.objects.filter(lesson=lesson)
            for content in content_lessons:
                self.stdout.write(f"  Content: {content.title_en} (type: {content.content_type})")
                
                # Check if this content has VocabularyList
                vocab_lists = VocabularyList.objects.filter(content_lesson=content)
                if vocab_lists.exists():
                    self.stdout.write(f"    Has {vocab_lists.count()} vocabulary lists")
                    for vl in vocab_lists:
                        self.stdout.write(f"      List {vl.id}: {vl.vocabularyitem_set.count()} items")