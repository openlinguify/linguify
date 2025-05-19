from django.core.management.base import BaseCommand
from django.db import transaction
from apps.course.models import TheoryContent, ContentLesson

class Command(BaseCommand):
    help = 'Fix TheoryContent creation issues and provide detailed diagnostics'

    def handle(self, *args, **options):
        self.stdout.write("=== TheoryContent Issue Diagnostics ===\n")
        
        # 1. Check for ContentLessons with default=1
        self.stdout.write("1. Checking default ContentLesson (ID=1):")
        try:
            default_lesson = ContentLesson.objects.get(id=1)
            self.stdout.write(f"   Found: {default_lesson}")
            self.stdout.write(f"   Type: {default_lesson.content_type}")
            self.stdout.write(f"   Lesson: {default_lesson.lesson}")
            
            # Check for existing TheoryContent
            existing_theory = TheoryContent.objects.filter(content_lesson_id=1).first()
            if existing_theory:
                self.stdout.write(self.style.WARNING(f"   Has TheoryContent: ID={existing_theory.id}"))
                self.stdout.write(f"   Created: {existing_theory.created_at if hasattr(existing_theory, 'created_at') else 'Unknown'}")
            else:
                self.stdout.write(self.style.SUCCESS("   No TheoryContent attached"))
        except ContentLesson.DoesNotExist:
            self.stdout.write(self.style.ERROR("   ContentLesson ID=1 not found"))
        
        # 2. List all ContentLessons with Theory type but no TheoryContent
        self.stdout.write("\n2. Theory-type ContentLessons without TheoryContent:")
        theory_lessons = ContentLesson.objects.filter(content_type='Theory')
        for lesson in theory_lessons:
            if not hasattr(lesson, 'theory_content'):
                self.stdout.write(f"   ID: {lesson.id} - {lesson.title_en} ({lesson.lesson})")
        
        # 3. Remove the database default
        self.stdout.write("\n3. Database default check:")
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_default 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'course_theorycontent' 
                AND column_name = 'content_lesson_id'
            """)
            result = cursor.fetchone()
            if result and result[0]:
                self.stdout.write(self.style.WARNING(f"   Default value found: {result[0]}"))
                # Optionally remove it
                if options.get('fix'):
                    cursor.execute("ALTER TABLE course_theorycontent ALTER COLUMN content_lesson_id DROP DEFAULT")
                    self.stdout.write(self.style.SUCCESS("   Default removed"))
            else:
                self.stdout.write("   No default value set")
        
        # 4. Create a test TheoryContent
        self.stdout.write("\n4. Testing TheoryContent creation:")
        available_lessons = ContentLesson.objects.filter(content_type='Theory').exclude(
            id__in=TheoryContent.objects.values_list('content_lesson_id', flat=True)
        ).first()
        
        if available_lessons:
            self.stdout.write(f"   Testing with ContentLesson ID: {available_lessons.id}")
            try:
                with transaction.atomic():
                    test_theory = TheoryContent.objects.create(
                        content_lesson=available_lessons,
                        content_en="Test content for diagnostics",
                        content_fr="Contenu test pour diagnostics",
                        content_es="Contenido de prueba para diagnósticos",
                        content_nl="Testinhoud voor diagnostiek",
                        explication_en="This is a test explanation to verify the creation process",
                        explication_fr="Ceci est une explication de test pour vérifier le processus de création",
                        explication_es="Esta es una explicación de prueba para verificar el proceso de creación",
                        explication_nl="Dit is een testuitleg om het creatieproces te verifiëren"
                    )
                    self.stdout.write(self.style.SUCCESS(f"   Created successfully! ID: {test_theory.id}"))
                    
                    # Rollback to not actually save it
                    raise Exception("Rolling back test creation")
            except Exception as e:
                if "Rolling back" not in str(e):
                    self.stdout.write(self.style.ERROR(f"   Creation failed: {e}"))
        else:
            self.stdout.write("   No available ContentLessons for testing")
        
        # 5. Summary and recommendations
        self.stdout.write("\n5. Recommendations:")
        self.stdout.write("   - Ensure ContentLesson is selected (not using default)")
        self.stdout.write("   - Check that the selected ContentLesson doesn't already have TheoryContent")
        self.stdout.write("   - Verify all required fields have substantial content (not single letters)")
        self.stdout.write("   - Use the template feature to auto-fill valid content")
        
        self.stdout.write("\nTo fix issues, run: python manage.py fix_theory_content_issues --fix")