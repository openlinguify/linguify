from django.core.management.base import BaseCommand
from apps.course.models import TheoryContent, ContentLesson

class Command(BaseCommand):
    help = 'Create TheoryContent directly to bypass admin Unicode issues'

    def add_arguments(self, parser):
        parser.add_argument('--content-lesson-id', type=int, help='ContentLesson ID')
        
    def handle(self, *args, **options):
        content_lesson_id = options.get('content_lesson_id')
        
        if not content_lesson_id:
            # Lister les ContentLessons disponibles
            self.stdout.write("Available ContentLessons without TheoryContent:")
            used_ids = TheoryContent.objects.values_list('content_lesson_id', flat=True)
            available = ContentLesson.objects.exclude(id__in=used_ids)
            
            for cl in available:
                self.stdout.write(f"  ID: {cl.id} - {cl.title_en} ({cl.content_type})")
            
            return
        
        # Créer le TheoryContent
        try:
            content_lesson = ContentLesson.objects.get(id=content_lesson_id)
            
            # Vérifier qu'il n'existe pas déjà
            if TheoryContent.objects.filter(content_lesson=content_lesson).exists():
                self.stdout.write(self.style.ERROR(f"TheoryContent already exists for ContentLesson {content_lesson_id}"))
                return
            
            # Créer avec le contenu sur les pluriels
            theory = TheoryContent.objects.create(
                content_lesson=content_lesson,
                content_en="Forming plural nouns in English",
                content_fr="Formation des noms au pluriel en français",
                content_es="Formación del plural en español",
                content_nl="Meervoudsvorming in het Nederlands",
                explication_en="In English, most plurals are formed by adding -s or -es to the end of a noun.",
                explication_fr="En français, la plupart des pluriels se forment en ajoutant -s à la fin du nom.",
                explication_es="En español, los plurales se forman añadiendo -s o -es según la terminación.",
                explication_nl="In het Nederlands worden meervouden gevormd door -en of -s toe te voegen.",
                formula_en="Singular + -s/-es = Plural",
                formula_fr="Singulier + -s = Pluriel",
                formula_es="Singular + -s/-es = Plural",
                formula_nl="Enkelvoud + -en/-s = Meervoud",
                example_en="cat → cats, box → boxes",
                example_fr="chat → chats, boîte → boîtes",
                example_es="gato → gatos, caja → cajas",
                example_nl="kat → katten, doos → dozen",
                using_json_format=False
            )
            
            self.stdout.write(self.style.SUCCESS(f"Created TheoryContent ID: {theory.id}"))
            
        except ContentLesson.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"ContentLesson with ID {content_lesson_id} not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))