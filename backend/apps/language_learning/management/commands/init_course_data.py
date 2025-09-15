from django.core.management.base import BaseCommand
from apps.language_learning.models import Language, CourseUnit, CourseModule


class Command(BaseCommand):
    help = 'Initialize course units and modules for each language'

    def handle(self, *args, **options):
        # Structure de cours pour chaque langue
        course_structures = {
            'en': {
                'units': [
                    {
                        'unit_number': 1,
                        'title': 'Getting Started',
                        'description': 'Basic greetings and introductions',
                        'modules': [
                            ('Greetings', 'vocabulary', 'Learn basic greetings and farewells'),
                            ('Introductions', 'speaking', 'Practice introducing yourself'),
                            ('Numbers 1-10', 'vocabulary', 'Learn to count from 1 to 10'),
                            ('Basic Grammar', 'grammar', 'Subject pronouns and "to be"'),
                        ]
                    },
                    {
                        'unit_number': 2,
                        'title': 'Daily Life',
                        'description': 'Essential vocabulary for everyday situations',
                        'modules': [
                            ('Family Members', 'vocabulary', 'Learn family vocabulary'),
                            ('Daily Routines', 'vocabulary', 'Common daily activities'),
                            ('Present Simple', 'grammar', 'Learn the present simple tense'),
                            ('Listening Practice', 'listening', 'Understand daily conversations'),
                        ]
                    },
                    {
                        'unit_number': 3,
                        'title': 'Food & Drink',
                        'description': 'Order food and talk about preferences',
                        'modules': [
                            ('Food Vocabulary', 'vocabulary', 'Common foods and drinks'),
                            ('At the Restaurant', 'speaking', 'Order food in a restaurant'),
                            ('Likes and Dislikes', 'grammar', 'Express preferences'),
                            ('Cultural Notes', 'culture', 'Dining etiquette in English-speaking countries'),
                        ]
                    },
                ]
            },
            'fr': {
                'units': [
                    {
                        'unit_number': 1,
                        'title': 'Premiers pas',
                        'description': 'Salutations et présentations de base',
                        'modules': [
                            ('Salutations', 'vocabulary', 'Apprendre les salutations de base'),
                            ('Se présenter', 'speaking', 'Pratiquer les présentations'),
                            ('Les nombres 1-10', 'vocabulary', 'Compter de 1 à 10'),
                            ('Grammaire de base', 'grammar', 'Les pronoms et le verbe être'),
                        ]
                    },
                    {
                        'unit_number': 2,
                        'title': 'La vie quotidienne',
                        'description': 'Vocabulaire essentiel pour le quotidien',
                        'modules': [
                            ('La famille', 'vocabulary', 'Le vocabulaire de la famille'),
                            ('Les routines', 'vocabulary', 'Les activités quotidiennes'),
                            ('Le présent', 'grammar', 'La conjugaison au présent'),
                            ('Compréhension orale', 'listening', 'Comprendre des conversations'),
                        ]
                    },
                    {
                        'unit_number': 3,
                        'title': 'Nourriture et boissons',
                        'description': 'Commander et parler de ses goûts',
                        'modules': [
                            ('Vocabulaire alimentaire', 'vocabulary', 'Aliments et boissons courants'),
                            ('Au restaurant', 'speaking', 'Commander au restaurant'),
                            ('Aimer et préférer', 'grammar', 'Exprimer ses préférences'),
                            ('Culture française', 'culture', 'La gastronomie française'),
                        ]
                    },
                ]
            },
            'es': {
                'units': [
                    {
                        'unit_number': 1,
                        'title': 'Primeros pasos',
                        'description': 'Saludos y presentaciones básicas',
                        'modules': [
                            ('Saludos', 'vocabulary', 'Aprender saludos básicos'),
                            ('Presentarse', 'speaking', 'Practicar presentaciones'),
                            ('Números 1-10', 'vocabulary', 'Contar del 1 al 10'),
                            ('Gramática básica', 'grammar', 'Pronombres y verbo ser/estar'),
                        ]
                    },
                    {
                        'unit_number': 2,
                        'title': 'La vida diaria',
                        'description': 'Vocabulario esencial para el día a día',
                        'modules': [
                            ('La familia', 'vocabulary', 'Vocabulario familiar'),
                            ('Rutinas diarias', 'vocabulary', 'Actividades cotidianas'),
                            ('Presente simple', 'grammar', 'Conjugación en presente'),
                            ('Comprensión auditiva', 'listening', 'Entender conversaciones'),
                        ]
                    },
                ]
            },
            'nl': {
                'units': [
                    {
                        'unit_number': 1,
                        'title': 'Eerste stappen',
                        'description': 'Begroetingen en basis introductie',
                        'modules': [
                            ('Begroetingen', 'vocabulary', 'Leer basis begroetingen'),
                            ('Jezelf voorstellen', 'speaking', 'Oefen introductie'),
                            ('Getallen 1-10', 'vocabulary', 'Tellen van 1 tot 10'),
                            ('Basis grammatica', 'grammar', 'Voornaamwoorden en zijn'),
                        ]
                    },
                    {
                        'unit_number': 2,
                        'title': 'Dagelijks leven',
                        'description': 'Essentiële woordenschat voor elke dag',
                        'modules': [
                            ('Familie', 'vocabulary', 'Familie woordenschat'),
                            ('Dagelijkse routines', 'vocabulary', 'Dagelijkse activiteiten'),
                            ('Tegenwoordige tijd', 'grammar', 'Werkwoorden in het heden'),
                            ('Luisteroefening', 'listening', 'Gesprekken begrijpen'),
                        ]
                    },
                ]
            }
        }

        for lang_code, course_data in course_structures.items():
            # Obtenir ou créer la langue
            language, _ = Language.objects.get_or_create(
                code=lang_code,
                defaults={'name': lang_code.upper(), 'is_active': True}
            )

            self.stdout.write(f"Processing language: {language.name}")

            for unit_data in course_data['units']:
                # Créer l'unité
                unit, created = CourseUnit.objects.get_or_create(
                    language=language,
                    unit_number=unit_data['unit_number'],
                    defaults={
                        'title': unit_data['title'],
                        'description': unit_data['description'],
                        'order': unit_data['unit_number'] * 10,
                        'is_active': True,
                    }
                )

                if created:
                    self.stdout.write(f"  Created unit: {unit.title}")
                else:
                    self.stdout.write(f"  Unit exists: {unit.title}")

                # Créer les modules
                for idx, (title, module_type, description) in enumerate(unit_data['modules'], 1):
                    module, created = CourseModule.objects.get_or_create(
                        unit=unit,
                        module_number=idx,
                        defaults={
                            'title': title,
                            'module_type': module_type,
                            'description': description,
                            'estimated_duration': 10 + (idx * 5),  # 15, 20, 25, 30 minutes
                            'xp_reward': 10 + (idx * 5),  # 15, 20, 25, 30 XP
                            'order': idx * 10,
                            'is_locked': idx > 1,  # Lock all except first module
                        }
                    )

                    if created:
                        self.stdout.write(f"    Created module: {module.title}")
                    else:
                        self.stdout.write(f"    Module exists: {module.title}")

        self.stdout.write(self.style.SUCCESS('Successfully initialized course data!'))