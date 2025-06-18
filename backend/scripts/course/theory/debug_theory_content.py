from django.core.management.base import BaseCommand
from django.db import connection
from apps.course.models import TheoryContent, ContentLesson

class Command(BaseCommand):
    help = 'Debug TheoryContent creation issues'

    def handle(self, *args, **options):
        self.stdout.write("=== Debug TheoryContent Creation ===")
        
        # 1. Check existing TheoryContent objects
        self.stdout.write("\n1. Existing TheoryContent objects:")
        theory_contents = TheoryContent.objects.all().select_related('content_lesson')
        for tc in theory_contents:
            self.stdout.write(f"   ID: {tc.id}, ContentLesson: {tc.content_lesson} (ID: {tc.content_lesson_id})")
        
        # 2. Check ContentLessons WITHOUT TheoryContent
        self.stdout.write("\n2. ContentLessons WITHOUT TheoryContent:")
        content_lessons_with_theory = TheoryContent.objects.values_list('content_lesson_id', flat=True)
        available_lessons = ContentLesson.objects.exclude(id__in=content_lessons_with_theory)
        
        for lesson in available_lessons:
            self.stdout.write(f"   ID: {lesson.id}, Type: {lesson.content_type}, Title: {lesson.title_en}")
        
        # 3. Check database constraints
        self.stdout.write("\n3. Database Constraints:")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT constraint_name, constraint_type 
                FROM information_schema.table_constraints 
                WHERE table_schema = 'public' 
                AND table_name = 'course_theorycontent'
            """)
            constraints = cursor.fetchall()
            for constraint in constraints:
                self.stdout.write(f"   {constraint[0]}: {constraint[1]}")
        
        # 4. Check the default ContentLesson (ID=1)
        self.stdout.write("\n4. Default ContentLesson (ID=1):")
        try:
            default_lesson = ContentLesson.objects.get(id=1)
            self.stdout.write(f"   Found: {default_lesson} - Type: {default_lesson.content_type}")
            
            # Check if it already has TheoryContent
            if hasattr(default_lesson, 'theory_content'):
                self.stdout.write(f"   Already has TheoryContent ID: {default_lesson.theory_content.id}")
            else:
                self.stdout.write("   No TheoryContent attached")
        except ContentLesson.DoesNotExist:
            self.stdout.write("   Not found!")
        
        # 5. Test creating a TheoryContent
        self.stdout.write("\n5. Testing TheoryContent creation:")
        if available_lessons.exists():
            test_lesson = available_lessons.first()
            self.stdout.write(f"   Using ContentLesson: {test_lesson} (ID: {test_lesson.id})")
            
            try:
                test_theory = TheoryContent.objects.create(
                    content_lesson=test_lesson,
                    content_en="Test content",
                    content_fr="Contenu test",
                    content_es="Contenido test",
                    content_nl="Test inhoud",
                    explication_en="Test explanation",
                    explication_fr="Explication test",
                    explication_es="Explicación test",
                    explication_nl="Test uitleg"
                )
                self.stdout.write(self.style.SUCCESS(f"   Success! Created TheoryContent ID: {test_theory.id}"))
                test_theory.delete()  # Clean up
                self.stdout.write("   Cleaned up test object")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   Failed: {e}"))
        else:
            self.stdout.write("   No available ContentLessons to test with")