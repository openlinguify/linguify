from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.course.models import ContentLesson, TheoryContent, Lesson
import json
import re
import os
import json

class Command(BaseCommand):
    help = 'Create theory lesson with smart title detection based on parent lesson'

    def add_arguments(self, parser):
        parser.add_argument('--lesson-id', type=int, required=True, help='The Lesson ID where to add the content')
        parser.add_argument('--auto-title', action='store_true', help='Automatically detect title from lesson context')
        parser.add_argument('--title', type=str, help='Manual title override')
        parser.add_argument('--template', type=str, help='Use a predefined template matching the topic')
        parser.add_argument('--order', type=int, help='Order in the lesson')
        parser.add_argument('--dry-run', action='store_true', help='Preview what would be created without creating anything')
        parser.add_argument('--list-templates', action='store_true', help='List available templates')
        
    def handle(self, *args, **options):
        # Liste des templates si demandé
        if options.get('list_templates'):
            self.list_available_templates()
            return
            
        lesson_id = options['lesson_id']
        auto_title = options.get('auto_title', True)
        manual_title = options.get('title')
        template = options.get('template')
        order = options.get('order')
        dry_run = options.get('dry_run', False)
        
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            raise CommandError(f'Lesson with ID {lesson_id} does not exist')
        
        # Determine title
        if manual_title:
            title = manual_title
        elif auto_title:
            title = self.extract_smart_title(lesson)
        else:
            title = "Theory"
        
        # Detect template if not specified
        if not template:
            template = self.detect_template_from_context(lesson, title)
        
        # Mode prévisualisation
        if dry_run:
            self.stdout.write(self.style.WARNING("\n=== DRY RUN MODE - Nothing will be created ==="))
        
        self.stdout.write(f"\n{'Previewing' if dry_run else 'Creating'} theory content for: {lesson}")
        self.stdout.write(f"Detected title: {title}")
        self.stdout.write(f"Using template: {template}")
        
        # Get content based on template
        theory_content = self.get_template_content(template, title)
        
        # Preview the content
        if dry_run:
            self.stdout.write("\nContent preview:")
            for lang, content in theory_content.items():
                self.stdout.write(f"\n{lang.upper()}:")
                if 'content' in content:
                    self.stdout.write(f"  Content: {content['content'][:100]}...")
                if 'explanation' in content:
                    self.stdout.write(f"  Explanation: {content['explanation'][:50]}...")
        
        # Determine order
        if order is None:
            max_order = ContentLesson.objects.filter(lesson=lesson).order_by('-order').first()
            order = (max_order.order + 1) if max_order else 1
        
        # Check if theory already exists
        existing = ContentLesson.objects.filter(
            lesson=lesson,
            content_type='Theory'
        ).first()
        
        if existing:
            self.stdout.write(self.style.WARNING(f"Theory already exists: {existing}"))
            if dry_run:
                self.stdout.write("Would NOT create new theory content.")
            return
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"\nWould create ContentLesson with:"))
            self.stdout.write(f"  Title EN: {title}")
            self.stdout.write(f"  Title FR: {self.translate_title(title, 'fr')}")
            self.stdout.write(f"  Title ES: {self.translate_title(title, 'es')}")
            self.stdout.write(f"  Title NL: {self.translate_title(title, 'nl')}")
            self.stdout.write(f"  Order: {order}")
            self.stdout.write(f"  Template: {template}")
            self.stdout.write(self.style.SUCCESS("\nNothing created (dry run mode)"))
            return
            
        # Create everything in a transaction
        with transaction.atomic():
            
            # Create ContentLesson
            content_lesson = ContentLesson.objects.create(
                lesson=lesson,
                content_type='Theory',
                title_en=title,
                title_fr=self.translate_title(title, 'fr'),
                title_es=self.translate_title(title, 'es'),
                title_nl=self.translate_title(title, 'nl'),
                order=order,
                estimated_duration=15
            )
            
            # Create TheoryContent
            theory = TheoryContent.objects.create(
                content_lesson=content_lesson,
                using_json_format=True,
                language_specific_content=theory_content,
                available_languages=list(theory_content.keys()),
                **self.extract_traditional_fields(theory_content)
            )
            
            self.stdout.write(self.style.SUCCESS(f"Created: {content_lesson}"))
            self.stdout.write(f"TheoryContent ID: {theory.id}")
    
    def extract_smart_title(self, lesson):
        """Extract intelligent title from lesson context"""
        # Get lesson title and parse it
        title_en = lesson.title_en
        
        # Common patterns in lesson titles
        patterns = [
            # Pattern: "Unit X - Topic - type"
            r'Unit \d+ - (.+?) - \w+$',
            # Pattern: "Topic - type"
            r'^(.+?) - \w+$',
            # Just get the main part before any dash
            r'^([^-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title_en)
            if match:
                topic = match.group(1).strip()
                # Clean up common suffixes
                topic = re.sub(r'\s*(vocabulary|grammar|lesson)\s*$', '', topic, flags=re.IGNORECASE)
                return topic
        
        # Fallback to just "Theory"
        return "Theory"
    
    def translate_title(self, title, lang):
        """Simple title translations"""
        translations = {
            'fr': {
                'Telling Time': 'Dire l\'heure',
                'Articles': 'Les articles',
                'Dates': 'Les dates',
                'Numbers': 'Les nombres',
                'Plurals': 'Les pluriels',
                'Present Simple': 'Le présent simple',
                'Past Simple': 'Le passé simple',
                'Colors': 'Les couleurs',
                'Family Members': 'Les membres de la famille',
                'Greetings': 'Les salutations',
                'Days and Months': 'Les jours et les mois',
            },
            'es': {
                'Telling Time': 'Decir la hora',
                'Articles': 'Los artículos',
                'Dates': 'Las fechas',
                'Numbers': 'Los números',
                'Plurals': 'Los plurales',
                'Present Simple': 'El presente simple',
                'Past Simple': 'El pasado simple',
                'Colors': 'Los colores',
                'Family Members': 'Los miembros de la familia',
                'Greetings': 'Los saludos',
                'Days and Months': 'Los días y los meses',
            },
            'nl': {
                'Telling Time': 'De tijd vertellen',
                'Articles': 'De lidwoorden',
                'Dates': 'De datums',
                'Numbers': 'De getallen',
                'Plurals': 'De meervouden',
                'Present Simple': 'De tegenwoordige tijd',
                'Past Simple': 'De verleden tijd',
                'Colors': 'De kleuren',
                'Family Members': 'De familieleden',
                'Greetings': 'De begroetingen',
                'Days and Months': 'De dagen en maanden',
            }
        }
        
        return translations.get(lang, {}).get(title, title)
    
    def detect_template_from_context(self, lesson, title):
        """Detect appropriate template based on lesson context"""
        title_lower = title.lower()
        lesson_title_lower = lesson.title_en.lower()
        
        # Map keywords to templates
        template_map = {
            'dates': ['date', 'calendar', 'day', 'month', 'year'],
            'time': ['time', 'hour', 'minute', 'clock', 'telling time'],
            'articles': ['article', 'un', 'une', 'le', 'la', 'les', 'the', 'a', 'an'],
            'plurals': ['plural', 'singular'],
            'numbers': ['number', 'counting', 'numeral'],
            'colors': ['color', 'colour'],
            'family': ['family', 'member', 'relative'],
            'greetings': ['greeting', 'hello', 'bye'],
            'pronouns': ['pronoun', 'i', 'you', 'he', 'she'],
            'verbs': ['verb', 'conjugation', 'tense'],
        }
        
        # Check both title and lesson title for keywords
        combined_text = f"{title_lower} {lesson_title_lower}"
        
        for template, keywords in template_map.items():
            for keyword in keywords:
                if keyword in combined_text:
                    return template
        
        return 'generic'
    
    def get_template_content(self, template, title):
        """Get template content based on detected template"""
        templates = {
            'articles': {
                "en": {
                    "content": f"Articles in English: definite (the) and indefinite (a, an)",
                    "explanation": "Articles are words that define a noun as specific or unspecific",
                    "formula": "Definite: THE\nIndefinite: A (before consonant), AN (before vowel)",
                    "example": "THE cat (specific cat)\nA cat (any cat)\nAN apple (before vowel sound)",
                    "exception": "No article with: plural general nouns, abstract nouns, proper nouns"
                },
                "fr": {
                    "content": f"Les articles en français : définis et indéfinis",
                    "explanation": "Les articles précèdent les noms et indiquent leur genre et nombre",
                    "formula": "Définis: LE, LA, LES\nIndéfinis: UN, UNE, DES",
                    "example": "LE chat (masculin)\nLA table (féminin)\nLES chats (pluriel)",
                    "exception": "Contraction: de + le = du, de + les = des"
                },
                "es": {
                    "content": f"Los artículos en español: definidos e indefinidos",
                    "explanation": "Los artículos preceden a los sustantivos e indican género y número",
                    "formula": "Definidos: EL, LA, LOS, LAS\nIndefinidos: UN, UNA, UNOS, UNAS",
                    "example": "EL gato (masculino)\nLA mesa (femenino)\nLOS gatos (plural)",
                    "exception": "Contracción: a + el = al, de + el = del"
                },
                "nl": {
                    "content": f"Lidwoorden in het Nederlands: bepaald en onbepaald",
                    "explanation": "Lidwoorden staan voor zelfstandige naamwoorden",
                    "formula": "Bepaald: DE, HET\nOnbepaald: EEN",
                    "example": "DE kat (de-woord)\nHET huis (het-woord)\nEEN kat (onbepaald)",
                    "exception": "Geen lidwoord bij: onbepaald meervoud, stofnamen, abstracte begrippen"
                }
            },
            'time': {
                "en": {
                    "content": f"{title} in English: expressing hours and minutes",
                    "explanation": "Different ways to express time in English",
                    "formula": "Digital: 3:30\nAnalog: half past three\nFormal: three thirty",
                    "example": "3:00 = three o'clock\n3:15 = quarter past three\n3:30 = half past three\n3:45 = quarter to four",
                    "exception": "Noon = 12:00 PM, Midnight = 12:00 AM"
                },
                "fr": {
                    "content": f"{self.translate_title(title, 'fr')} : exprimer les heures",
                    "explanation": "Les différentes façons d'exprimer l'heure en français",
                    "formula": "Formelle: 15h30\nCourante: trois heures et demie",
                    "example": "3h00 = trois heures\n3h15 = trois heures et quart\n3h30 = trois heures et demie\n3h45 = quatre heures moins le quart",
                    "exception": "Midi = 12h00, Minuit = 00h00"
                },
                "es": {
                    "content": f"{self.translate_title(title, 'es')}: expresar las horas",
                    "explanation": "Las diferentes formas de expresar la hora en español",
                    "formula": "Formal: las 15:30\nColoquial: las tres y media",
                    "example": "3:00 = las tres\n3:15 = las tres y cuarto\n3:30 = las tres y media\n3:45 = las cuatro menos cuarto",
                    "exception": "Mediodía = 12:00, Medianoche = 00:00"
                },
                "nl": {
                    "content": f"{self.translate_title(title, 'nl')}: uren en minuten uitdrukken",
                    "explanation": "Verschillende manieren om de tijd uit te drukken",
                    "formula": "Digitaal: 15:30\nAnaloog: half vier",
                    "example": "3:00 = drie uur\n3:15 = kwart over drie\n3:30 = half vier\n3:45 = kwart voor vier",
                    "exception": "'s Middags = 12:00, Middernacht = 00:00"
                }
            },
            'generic': {
                "en": {
                    "content": f"{title}: fundamental concepts and rules",
                    "explanation": f"Understanding the basics of {title.lower()}",
                    "formula": "Key patterns and rules",
                    "example": "Common examples and usage",
                    "exception": "Special cases and exceptions"
                },
                "fr": {
                    "content": f"{self.translate_title(title, 'fr')} : concepts fondamentaux",
                    "explanation": f"Comprendre les bases de {self.translate_title(title, 'fr').lower()}",
                    "formula": "Règles et modèles clés",
                    "example": "Exemples courants d'utilisation",
                    "exception": "Cas spéciaux et exceptions"
                },
                "es": {
                    "content": f"{self.translate_title(title, 'es')}: conceptos fundamentales",
                    "explanation": f"Entender los fundamentos de {self.translate_title(title, 'es').lower()}",
                    "formula": "Reglas y patrones clave",
                    "example": "Ejemplos comunes de uso",
                    "exception": "Casos especiales y excepciones"
                },
                "nl": {
                    "content": f"{self.translate_title(title, 'nl')}: fundamentele concepten",
                    "explanation": f"De basis begrijpen van {self.translate_title(title, 'nl').lower()}",
                    "formula": "Belangrijke regels en patronen",
                    "example": "Veelvoorkomende voorbeelden",
                    "exception": "Speciale gevallen en uitzonderingen"
                }
            }
        }
        
        # Return template or generic if not found
        return templates.get(template, templates['generic'])
    
    def extract_traditional_fields(self, content):
        """Extract traditional fields from JSON content"""
        fields = {}
        for lang in ['en', 'fr', 'es', 'nl']:
            if lang in content:
                fields[f'content_{lang}'] = content[lang].get('content', '')
                fields[f'explication_{lang}'] = content[lang].get('explanation', '')
                fields[f'formula_{lang}'] = content[lang].get('formula', '')
                fields[f'example_{lang}'] = content[lang].get('example', '')
                fields[f'exception_{lang}'] = content[lang].get('exception', '')
        return fields
    
    def list_available_templates(self):
        """Liste tous les templates disponibles"""
        self.stdout.write(self.style.SUCCESS("\n=== Available Templates ===\n"))
        
        # Templates intégrés dans le code
        code_templates = {
            'articles': 'Articles theory (the, a, an, le, la, un, une)',
            'dates': 'Dates and calendar vocabulary',
            'generic': 'Generic template (default)'
        }
        
        self.stdout.write("Built-in templates:")
        for template, desc in code_templates.items():
            self.stdout.write(f"  - {template}: {desc}")
        
        # Templates JSON dans le dossier
        self.stdout.write("\nFile-based templates:")
        template_dir = os.path.join(os.path.dirname(__file__), '../../templates/json')
        
        if os.path.exists(template_dir):
            for file in os.listdir(template_dir):
                if file.endswith('_theory.json'):
                    template_name = file.replace('_theory.json', '')
                    file_path = os.path.join(template_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = json.load(f)
                            # Essayer d'extraire une description du contenu
                            desc = ""
                            if 'en' in content and 'content' in content['en']:
                                desc = content['en']['content'][:50] + "..."
                            self.stdout.write(f"  - {template_name}: {desc}")
                    except Exception as e:
                        self.stdout.write(f"  - {template_name}: (Error reading: {e})")
        else:
            self.stdout.write("  (No template files found)")
        
        self.stdout.write("\nUsage: python manage.py create_smart_theory_lesson --lesson-id X --template TEMPLATE_NAME")