from django.core.management.base import BaseCommand
from apps.course.models import Unit, Chapter, Lesson, ContentLesson, VocabularyList

class Command(BaseCommand):
    help = 'Debug course data - shows what exists in the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== COURSE DATA DEBUG ==='))
        
        # Count everything
        units_count = Unit.objects.count()
        chapters_count = Chapter.objects.count()
        lessons_count = Lesson.objects.count()
        content_lessons_count = ContentLesson.objects.count()
        
        self.stdout.write(f"Units: {units_count}")
        self.stdout.write(f"Chapters: {chapters_count}")
        self.stdout.write(f"Lessons: {lessons_count}")
        self.stdout.write(f"Content Lessons: {content_lessons_count}")
        
        # Show first 5 units
        self.stdout.write(self.style.WARNING('\n=== UNITS ==='))
        for unit in Unit.objects.all()[:5]:
            self.stdout.write(f"Unit {unit.id}: {unit.title} ({unit.level})")
            
        # Show first 10 chapters
        self.stdout.write(self.style.WARNING('\n=== CHAPTERS ==='))
        for chapter in Chapter.objects.all()[:10]:
            lessons_in_chapter = chapter.lessons.count()
            self.stdout.write(f"Chapter {chapter.id}: {chapter.title} (Unit: {chapter.unit.title}) - {lessons_in_chapter} lessons")
            
        # Show first 10 lessons
        self.stdout.write(self.style.WARNING('\n=== LESSONS ==='))
        for lesson in Lesson.objects.all()[:10]:
            chapter_name = lesson.chapter.title if lesson.chapter else "No Chapter"
            content_count = lesson.content_lessons.count()
            self.stdout.write(f"Lesson {lesson.id}: {lesson.title} (Chapter: {chapter_name}) - {content_count} content items")
            
        # Show lesson-chapter relationships
        self.stdout.write(self.style.WARNING('\n=== LESSON-CHAPTER RELATIONSHIPS ==='))
        lessons_with_chapter = Lesson.objects.filter(chapter__isnull=False).count()
        lessons_without_chapter = Lesson.objects.filter(chapter__isnull=True).count()
        self.stdout.write(f"Lessons with chapter: {lessons_with_chapter}")
        self.stdout.write(f"Lessons without chapter: {lessons_without_chapter}")
        
        # Show content breakdown
        self.stdout.write(self.style.WARNING('\n=== CONTENT BREAKDOWN ==='))
        for content_type in ['vocabulary', 'grammar', 'theory', 'matching', 'Test Recap']:
            count = ContentLesson.objects.filter(content_type=content_type).count()
            self.stdout.write(f"{content_type}: {count}")
            
        self.stdout.write(self.style.SUCCESS('\n=== DEBUG COMPLETE ==='))