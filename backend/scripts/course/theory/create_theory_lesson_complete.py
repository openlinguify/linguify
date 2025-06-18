from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.course.models import ContentLesson, TheoryContent, Lesson
import json

class Command(BaseCommand):
    help = 'Create a complete theory lesson with ContentLesson and TheoryContent in one command'

    def add_arguments(self, parser):
        parser.add_argument('--lesson-id', type=int, required=True, help='The Lesson ID where to add the content')
        parser.add_argument('--title', type=str, required=True, help='The title for the content lesson')
        parser.add_argument('--template', type=str, choices=['dates', 'plurals', 'custom'], default='custom', 
                          help='Use a predefined template or create custom content')
        parser.add_argument('--json-file', type=str, help='Path to JSON file with theory content')
        parser.add_argument('--order', type=int, help='Order in the lesson (auto-incremented if not specified)')
        
    def handle(self, *args, **options):
        lesson_id = options['lesson_id']
        title = options['title']
        template = options['template']
        json_file = options.get('json_file')
        order = options.get('order')
        
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            raise CommandError(f'Lesson with ID {lesson_id} does not exist')
        
        # Determine order
        if order is None:
            max_order = ContentLesson.objects.filter(lesson=lesson).order_by('-order').first()
            order = (max_order.order + 1) if max_order else 1
        
        self.stdout.write(f"Creating theory content for: {lesson} - Order: {order}")
        
        # Load content based on template or file
        if template == 'dates':
            theory_content = self.get_dates_template()
        elif template == 'plurals':
            theory_content = self.get_plurals_template()
        elif json_file:
            with open(json_file, 'r', encoding='utf-8') as f:
                theory_content = json.load(f)
        else:
            theory_content = self.get_empty_template()
        
        # Create everything in a transaction
        with transaction.atomic():
            # 1. Create ContentLesson
            content_lesson = ContentLesson.objects.create(
                lesson=lesson,
                content_type='Theory',
                title_en=title,
                title_fr=title,
                title_es=title,
                title_nl=title,
                order=order,
                estimated_duration=15  # Default duration for theory
            )
            
            self.stdout.write(f"Created ContentLesson ID: {content_lesson.id}")
            
            # 2. Create TheoryContent
            theory = TheoryContent.objects.create(
                content_lesson=content_lesson,
                using_json_format=True,
                language_specific_content=theory_content,
                available_languages=list(theory_content.keys()),
                # Also fill traditional fields from JSON
                content_en=theory_content.get('en', {}).get('content', ''),
                content_fr=theory_content.get('fr', {}).get('content', ''),
                content_es=theory_content.get('es', {}).get('content', ''),
                content_nl=theory_content.get('nl', {}).get('content', ''),
                explication_en=theory_content.get('en', {}).get('explanation', ''),
                explication_fr=theory_content.get('fr', {}).get('explanation', ''),
                explication_es=theory_content.get('es', {}).get('explanation', ''),
                explication_nl=theory_content.get('nl', {}).get('explanation', ''),
                formula_en=theory_content.get('en', {}).get('formula', ''),
                formula_fr=theory_content.get('fr', {}).get('formula', ''),
                formula_es=theory_content.get('es', {}).get('formula', ''),
                formula_nl=theory_content.get('nl', {}).get('formula', ''),
                example_en=theory_content.get('en', {}).get('example', ''),
                example_fr=theory_content.get('fr', {}).get('example', ''),
                example_es=theory_content.get('es', {}).get('example', ''),
                example_nl=theory_content.get('nl', {}).get('example', ''),
                exception_en=theory_content.get('en', {}).get('exception', ''),
                exception_fr=theory_content.get('fr', {}).get('exception', ''),
                exception_es=theory_content.get('es', {}).get('exception', ''),
                exception_nl=theory_content.get('nl', {}).get('exception', '')
            )
            
            self.stdout.write(self.style.SUCCESS(f"Created TheoryContent ID: {theory.id}"))
            self.stdout.write(f"Complete theory lesson created successfully!")
            self.stdout.write(f"ContentLesson: {content_lesson}")
            self.stdout.write(f"TheoryContent: {theory}")
    
    def get_empty_template(self):
        return {
            "en": {
                "content": "Content to be filled",
                "explanation": "Explanation to be filled",
                "formula": "",
                "example": "",
                "exception": ""
            },
            "fr": {
                "content": "Contenu à remplir",
                "explanation": "Explication à remplir",
                "formula": "",
                "example": "",
                "exception": ""
            },
            "es": {
                "content": "Contenido a rellenar",
                "explanation": "Explicación a rellenar",
                "formula": "",
                "example": "",
                "exception": ""
            },
            "nl": {
                "content": "Inhoud om in te vullen",
                "explanation": "Uitleg om in te vullen",
                "formula": "",
                "example": "",
                "exception": ""
            }
        }
    
    def get_dates_template(self):
        return {
            "en": {
                "content": "Learning how to express dates in English involves understanding days of the week, months of the year, and the different date formats used in various English-speaking countries.",
                "example": "Days: Monday-Sunday\nMonths: January-December\nAmerican: 03/15/2024\nBritish: 15/03/2024",
                "formula": "American: MM/DD/YYYY\nBritish: DD/MM/YYYY\nInternational: YYYY-MM-DD",
                "exception": "Ordinal numbers: 1st, 2nd, 3rd, then -th\nAmerican vs British spelling differences",
                "explanation": "Understanding date formats is crucial for international communication and avoiding confusion."
            },
            "fr": {
                "content": "Apprendre à exprimer les dates en français implique de maîtriser les jours de la semaine, les mois de l'année et le format de date standard.",
                "example": "Jours : lundi-dimanche\nMois : janvier-décembre\nFormat : 15/03/2024",
                "formula": "Standard : JJ/MM/AAAA\nComplet : le jour mois année",
                "exception": "Premier jour : 'le premier' (jamais 'le un')\nPas de majuscules pour jours/mois",
                "explanation": "Le format de date français est cohérent dans tous les pays francophones."
            },
            "es": {
                "content": "Aprender a expresar fechas en español implica comprender los días de la semana, los meses del año y el formato estándar.",
                "example": "Días: lunes-domingo\nMeses: enero-diciembre\nFormato: 15/03/2024",
                "formula": "Estándar: DD/MM/AAAA\nCompleto: día de mes de año",
                "exception": "Primer día: 'primero' o 'uno'\nMinúsculas para días/meses",
                "explanation": "El formato español es consistente en todos los países hispanohablantes."
            },
            "nl": {
                "content": "Het leren uitdrukken van datums in het Nederlands omvat dagen van de week, maanden en het standaard datumformaat.",
                "example": "Dagen: maandag-zondag\nMaanden: januari-december\nFormaat: 15-03-2024",
                "formula": "Standaard: DD-MM-JJJJ\nVolledig: dag maand jaar",
                "exception": "Eerste dag: 'eerste' of '1'\nKleine letters voor dagen/maanden",
                "explanation": "Het Nederlandse datumformaat gebruikt koppeltekens in plaats van schuine strepen."
            }
        }
    
    def get_plurals_template(self):
        return {
            "en": {
                "content": "In English, plurals are usually formed by adding -s or -es to the end of a noun.",
                "example": "cat → cats\nbox → boxes\ncity → cities",
                "formula": "Add -s to most nouns\nAdd -es to nouns ending in -s, -ss, -sh, -ch, -x",
                "exception": "Irregular: man → men, child → children\nSame form: sheep, deer, fish",
                "explanation": "Understanding plurals affects noun-verb agreement in sentences."
            },
            "fr": {
                "content": "En français, les pluriels sont généralement formés en ajoutant -s à la fin du nom.",
                "example": "chat → chats\nbateau → bateaux\njournal → journaux",
                "formula": "Ajouter -s à la plupart des noms\n-au/-eau → -aux\n-al → -aux",
                "exception": "Exceptions: œil → yeux, travail → travaux",
                "explanation": "Les pluriels affectent l'accord des adjectifs et des verbes."
            },
            "es": {
                "content": "En español, los plurales se forman añadiendo -s o -es según la terminación.",
                "example": "gato → gatos\nvoz → voces\nciudad → ciudades",
                "formula": "Añadir -s si termina en vocal\nAñadir -es si termina en consonante",
                "exception": "Sin cambio: crisis, análisis\n-z → -ces: luz → luces",
                "explanation": "Los plurales afectan la concordancia con adjetivos."
            },
            "nl": {
                "content": "In het Nederlands worden meervouden gevormd met -en of -s.",
                "example": "kat → katten\nauto → auto's\nkind → kinderen",
                "formula": "Voeg -en toe aan meeste woorden\nVoeg -s toe na klinkers",
                "exception": "Onregelmatig: kind → kinderen\nKlinkerverandering: stad → steden",
                "explanation": "Meervouden beïnvloeden werkwoordsvervoegingen."
            }
        }
    