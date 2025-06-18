from django.core.management.base import BaseCommand
from apps.course.models import TheoryContent, ContentLesson
import json

class Command(BaseCommand):
    help = 'Full diagnostic of TheoryContent issues'

    def handle(self, *args, **options):
        self.stdout.write("=== Full TheoryContent Diagnostic ===\n")
        
        # 1. Lister tous les TheoryContent existants
        self.stdout.write("1. Existing TheoryContent objects:")
        theory_contents = TheoryContent.objects.all().select_related('content_lesson__lesson')
        
        for tc in theory_contents:
            self.stdout.write(f"\n   TheoryContent ID: {tc.id}")
            self.stdout.write(f"   ContentLesson: {tc.content_lesson} (ID: {tc.content_lesson_id})")
            self.stdout.write(f"   Using JSON format: {tc.using_json_format}")
            if tc.using_json_format and tc.language_specific_content:
                self.stdout.write(f"   Languages: {tc.available_languages}")
                self.stdout.write("   JSON content preview:")
                try:
                    json_preview = json.dumps(tc.language_specific_content, indent=2)[:200]
                    self.stdout.write(f"   {json_preview}...")
                except:
                    self.stdout.write("   [Error reading JSON]")
            else:
                self.stdout.write(f"   Content EN: {tc.content_en[:50]}..." if tc.content_en else "   Content EN: [empty]")
                self.stdout.write(f"   Content FR: {tc.content_fr[:50]}..." if tc.content_fr else "   Content FR: [empty]")
        
        if not theory_contents:
            self.stdout.write("   No TheoryContent objects found")
        
        # 2. Lister tous les ContentLessons disponibles
        self.stdout.write("\n2. Available ContentLessons (without TheoryContent):")
        used_lessons = TheoryContent.objects.values_list('content_lesson_id', flat=True)
        available_lessons = ContentLesson.objects.exclude(id__in=used_lessons).select_related('lesson')
        
        for lesson in available_lessons:
            self.stdout.write(f"   ID: {lesson.id} - {lesson.title_en} ({lesson.content_type}) - Lesson: {lesson.lesson}")
        
        if not available_lessons:
            self.stdout.write("   No available ContentLessons")
        
        # 3. ContentLessons de type Theory spécifiquement
        self.stdout.write("\n3. Theory-type ContentLessons:")
        theory_lessons = ContentLesson.objects.filter(content_type='Theory')
        
        for lesson in theory_lessons:
            has_content = TheoryContent.objects.filter(content_lesson=lesson).exists()
            status = "HAS TheoryContent" if has_content else "NO TheoryContent"
            self.stdout.write(f"   ID: {lesson.id} - {lesson.title_en} - {status}")
        
        # 4. Vérifier ContentLesson ID=1
        self.stdout.write("\n4. ContentLesson ID=1 check:")
        try:
            lesson_1 = ContentLesson.objects.get(id=1)
            self.stdout.write(f"   Found: {lesson_1}")
            theory_1 = TheoryContent.objects.filter(content_lesson_id=1).first()
            if theory_1:
                self.stdout.write(f"   Has TheoryContent: ID={theory_1.id}")
            else:
                self.stdout.write("   No TheoryContent")
        except ContentLesson.DoesNotExist:
            self.stdout.write("   Not found")
        
        # 5. Créer un exemple de TheoryContent valide
        self.stdout.write("\n5. Example of valid TheoryContent creation:")
        self.stdout.write("""
   For Traditional format:
   - content_en: "Days of the week and months in English"
   - content_fr: "Les jours de la semaine et les mois en français"
   - content_es: "Los días de la semana y los meses en español" 
   - content_nl: "Dagen van de week en maanden in het Nederlands"
   - explication_en: "English uses specific names for days and months with capital letters"
   - explication_fr: "Le français utilise des noms spécifiques pour les jours et mois"
   - explication_es: "El español usa nombres específicos para días y meses"
   - explication_nl: "Het Nederlands gebruikt specifieke namen voor dagen en maanden"
   
   For JSON format:
   - Check "Using json format"
   - Use the template feature or fill:
   {
     "en": {"content": "Days and months", "explanation": "English date formats"},
     "fr": {"content": "Jours et mois", "explanation": "Formats de date français"},
     "es": {"content": "Días y meses", "explanation": "Formatos de fecha españoles"},
     "nl": {"content": "Dagen en maanden", "explanation": "Nederlandse datumformaten"}
   }
        """)
        
        # 6. Résumé des problèmes potentiels
        self.stdout.write("\n6. Common Issues:")
        self.stdout.write("   - ContentLesson already has TheoryContent (OneToOne constraint)")
        self.stdout.write("   - JSON format enabled but content is null or empty")
        self.stdout.write("   - Required fields have minimal content (e.g., single letter 'f')")
        self.stdout.write("   - Default ContentLesson ID=1 is automatically selected")
        
        self.stdout.write("\n7. Solutions:")
        self.stdout.write("   - Select a different ContentLesson without TheoryContent")
        self.stdout.write("   - Use the template feature to auto-fill valid content")
        self.stdout.write("   - Disable JSON format for simpler creation")
        self.stdout.write("   - Ensure all required fields have substantial content")