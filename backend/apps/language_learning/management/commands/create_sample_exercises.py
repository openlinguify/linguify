"""
Commande de gestion pour créer des données d'exemple avec de vrais exercices
"""
from django.core.management.base import BaseCommand
from apps.language_learning.models import Language, CourseUnit, CourseModule


class Command(BaseCommand):
    help = 'Crée des unités et modules avec de vrais exercices pour tester le système'

    def add_arguments(self, parser):
        parser.add_argument(
            '--language',
            type=str,
            default='ES',
            help='Code de la langue pour laquelle créer les exercices (ES, FR, EN, etc.)'
        )

    def handle(self, *args, **options):
        language_code = options['language']

        try:
            language = Language.objects.get(code=language_code)
        except Language.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Langue {language_code} non trouvée. Création...')
            )
            language = Language.objects.create(
                code=language_code,
                name='Español' if language_code == 'ES' else 'Français' if language_code == 'FR' else 'English',
                native_name='Español' if language_code == 'ES' else 'Français' if language_code == 'FR' else 'English',
                flag_emoji='🇪🇸' if language_code == 'ES' else '🇫🇷' if language_code == 'FR' else '🇬🇧',
                is_active=True
            )

        # Créer l'unité "Básicos" si elle n'existe pas
        unit, created = CourseUnit.objects.get_or_create(
            language=language,
            unit_number=1,
            defaults={
                'title': 'Básicos' if language_code == 'ES' else 'Les bases' if language_code == 'FR' else 'Basics',
                'description': 'Apprendre les bases de la langue' if language_code == 'ES' else 'Apprendre les bases' if language_code == 'FR' else 'Learn the basics',
                'icon': 'bi-book',
                'color': '#10b981',
                'is_active': True,
                'order': 1
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Unité "{unit.title}" créée')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Unité "{unit.title}" existe déjà')
            )

        # Créer les modules avec des exercices spécifiques par langue
        if language_code == 'ES':
            modules_data = self.get_spanish_modules()
        elif language_code == 'FR':
            modules_data = self.get_french_modules()
        else:
            modules_data = self.get_english_modules()

        for module_data in modules_data:
            module, created = CourseModule.objects.get_or_create(
                unit=unit,
                module_number=module_data['module_number'],
                defaults=module_data
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Module "{module.title}" créé avec {len(module.content.get("exercises", []))} exercices')
                )
            else:
                # Mettre à jour le contenu si le module existe déjà
                module.content = module_data['content']
                module.save()
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Module "{module.title}" mis à jour avec {len(module.content.get("exercises", []))} exercices')
                )

        self.stdout.write(
            self.style.SUCCESS(f'🎉 Création terminée pour la langue {language_code}!')
        )

    def get_spanish_modules(self):
        """Retourne les données des modules espagnols avec de vrais exercices"""
        return [
            {
                'title': 'Saludos',
                'module_type': 'vocabulary',
                'description': 'Apprendre les salutations de base',
                'estimated_duration': 15,
                'xp_reward': 20,
                'is_locked': False,
                'order': 1,
                'content': {
                    "exercises": [
                        {
                            "type": "multiple_choice",
                            "question": "Comment dit-on 'Bonjour' en espagnol ?",
                            "prompt": "Choisissez la bonne réponse",
                            "options": ["Hola", "Adiós", "Gracias", "Por favor"],
                            "correct_answer": "Hola",
                            "explanation": "Hola est la salutation la plus courante en espagnol."
                        },
                        {
                            "type": "translation",
                            "text_to_translate": "Good morning",
                            "correct_answer": ["Buenos días", "Buen día"],
                            "explanation": "Buenos días est la salutation formelle du matin en espagnol."
                        },
                        {
                            "type": "fill_blank",
                            "question": "Complétez la salutation du soir",
                            "sentence_with_blank": "_____ noches. ¿Cómo está usted?",
                            "placeholder": "salutation du soir",
                            "correct_answer": ["Buenas"],
                            "explanation": "Buenas noches signifie 'bonne soirée/bonne nuit' en espagnol."
                        },
                        {
                            "type": "multiple_choice",
                            "question": "Que signifie 'Hasta luego' ?",
                            "prompt": "Choisissez la bonne traduction",
                            "options": ["Bonjour", "À bientôt", "Merci", "S'il vous plaît"],
                            "correct_answer": "À bientôt",
                            "explanation": "Hasta luego est une façon informelle de dire au revoir."
                        }
                    ]
                }
            },
            {
                'title': 'Presentaciones',
                'module_type': 'grammar',
                'description': 'Se présenter en espagnol',
                'estimated_duration': 15,
                'xp_reward': 20,
                'is_locked': False,
                'order': 2,
                'content': {
                    "exercises": [
                        {
                            "type": "fill_blank",
                            "question": "Conjuguez le verbe 'ser' à la première personne",
                            "sentence_with_blank": "Yo _____ estudiante.",
                            "placeholder": "verbe ser",
                            "correct_answer": ["soy"],
                            "explanation": "Soy est la conjugaison du verbe ser à la première personne du singulier."
                        },
                        {
                            "type": "multiple_choice",
                            "question": "Quel est l'article défini pour 'casa' (maison) ?",
                            "prompt": "Choisissez l'article correct",
                            "options": ["la", "el", "los", "las"],
                            "correct_answer": "la",
                            "explanation": "Casa est un nom féminin, donc on utilise l'article la."
                        },
                        {
                            "type": "translation",
                            "text_to_translate": "My name is Maria",
                            "correct_answer": ["Me llamo María", "Mi nombre es María"],
                            "explanation": "On peut dire 'Me llamo' ou 'Mi nombre es' pour dire son nom en espagnol."
                        },
                        {
                            "type": "fill_blank",
                            "question": "Complétez la présentation",
                            "sentence_with_blank": "Mucho _____ conocerte.",
                            "placeholder": "plaisir",
                            "correct_answer": ["gusto"],
                            "explanation": "Mucho gusto signifie 'enchanté' ou 'ravi de vous rencontrer'."
                        }
                    ]
                }
            },
            {
                'title': 'Números',
                'module_type': 'vocabulary',
                'description': 'Les nombres de 1 à 20',
                'estimated_duration': 15,
                'xp_reward': 20,
                'is_locked': False,
                'order': 3,
                'content': {
                    "exercises": [
                        {
                            "type": "multiple_choice",
                            "question": "Comment dit-on '5' en espagnol ?",
                            "prompt": "Choisissez la bonne réponse",
                            "options": ["cuatro", "cinco", "seis", "siete"],
                            "correct_answer": "cinco",
                            "explanation": "Cinco signifie 5 en espagnol."
                        },
                        {
                            "type": "translation",
                            "text_to_translate": "twelve",
                            "correct_answer": ["doce"],
                            "explanation": "Doce signifie douze en espagnol."
                        },
                        {
                            "type": "fill_blank",
                            "question": "Complétez la séquence",
                            "sentence_with_blank": "Ocho, nueve, _____",
                            "placeholder": "nombre suivant",
                            "correct_answer": ["diez"],
                            "explanation": "Après ocho (8) et nueve (9) vient diez (10)."
                        },
                        {
                            "type": "multiple_choice",
                            "question": "Quel nombre vient après 'quince' ?",
                            "prompt": "Choisissez le nombre suivant",
                            "options": ["catorce", "dieciséis", "diecisiete", "dieciocho"],
                            "correct_answer": "dieciséis",
                            "explanation": "Après quince (15) vient dieciséis (16)."
                        }
                    ]
                }
            },
            {
                'title': 'Práctica',
                'module_type': 'review',
                'description': 'Révision des bases',
                'estimated_duration': 15,
                'xp_reward': 20,
                'is_locked': False,
                'order': 4,
                'content': {
                    "exercises": [
                        {
                            "type": "translation",
                            "text_to_translate": "Hello, my name is Pedro and I am 25 years old",
                            "correct_answer": ["Hola, me llamo Pedro y tengo 25 años", "Hola, mi nombre es Pedro y tengo 25 años"],
                            "explanation": "Cette phrase combine salutations, présentation et âge."
                        },
                        {
                            "type": "fill_blank",
                            "question": "Complétez le dialogue",
                            "sentence_with_blank": "- ¿Cómo te llamas? - Me _____ Ana.",
                            "placeholder": "verbe manquant",
                            "correct_answer": ["llamo"],
                            "explanation": "Me llamo est la façon standard de dire son nom."
                        },
                        {
                            "type": "multiple_choice",
                            "question": "Quelle est la bonne réponse à '¿Cuántos años tienes?' ?",
                            "prompt": "Choisissez la réponse appropriée",
                            "options": ["Tengo veinte años", "Me llamo Juan", "Soy estudiante", "Hasta luego"],
                            "correct_answer": "Tengo veinte años",
                            "explanation": "¿Cuántos años tienes? demande l'âge, on répond avec 'Tengo ... años'."
                        }
                    ]
                }
            }
        ]

    def get_french_modules(self):
        """Retourne les données des modules français avec de vrais exercices"""
        return [
            {
                'title': 'Les salutations',
                'module_type': 'vocabulary',
                'description': 'Apprendre à saluer en français',
                'estimated_duration': 15,
                'xp_reward': 20,
                'is_locked': False,
                'order': 1,
                'content': {
                    "exercises": [
                        {
                            "type": "multiple_choice",
                            "question": "Comment dit-on 'Hello' en français ?",
                            "prompt": "Choisissez la bonne réponse",
                            "options": ["Bonjour", "Au revoir", "Merci", "S'il vous plaît"],
                            "correct_answer": "Bonjour",
                            "explanation": "Bonjour est la salutation standard en français."
                        },
                        {
                            "type": "translation",
                            "text_to_translate": "Good evening",
                            "correct_answer": ["Bonsoir"],
                            "explanation": "Bonsoir s'utilise le soir pour saluer."
                        }
                    ]
                }
            }
        ]

    def get_english_modules(self):
        """Retourne les données des modules anglais avec de vrais exercices"""
        return [
            {
                'title': 'Greetings',
                'module_type': 'vocabulary',
                'description': 'Learn basic greetings',
                'estimated_duration': 15,
                'xp_reward': 20,
                'is_locked': False,
                'order': 1,
                'content': {
                    "exercises": [
                        {
                            "type": "multiple_choice",
                            "question": "How do you say 'Bonjour' in English?",
                            "prompt": "Choose the correct answer",
                            "options": ["Hello", "Goodbye", "Thank you", "Please"],
                            "correct_answer": "Hello",
                            "explanation": "Hello is the standard greeting in English."
                        }
                    ]
                }
            }
        ]