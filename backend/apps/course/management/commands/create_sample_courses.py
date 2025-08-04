from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.course.models.core import Unit, Chapter, Lesson, ContentLesson


class Command(BaseCommand):
    help = 'Crée des cours d\'exemple pour tester l\'interface'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime tous les cours existants avant de créer les nouveaux',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Suppression des cours existants...')
            Unit.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cours supprimés'))

        self.stdout.write('Création des cours d\'exemple...')

        # Cours 1: Français pour Débutants (A1)
        unit_fr_a1 = Unit.objects.create(
            title_fr="Français pour Débutants",
            title_en="French for Beginners",
            description_fr="Apprenez les bases du français avec ce cours complet pour débutants. Vocabulaire essentiel, grammaire de base et expressions courantes.",
            description_en="Learn the basics of French with this complete beginner course. Essential vocabulary, basic grammar and common expressions.",
            level='A1',
            order=1,
            teacher_cms_id=1,
            is_published=True
        )

        # Chapitre 1 du cours de français
        chapter_fr_1 = Chapter.objects.create(
            unit=unit_fr_a1,
            title_fr="Se présenter",
            title_en="Introducing yourself",
            description_fr="Apprenez à vous présenter et à saluer en français",
            description_en="Learn to introduce yourself and greet in French",
            theme="introduction",
            order=1,
            style="Open Linguify",
            points_reward=100
        )

        # Leçons du chapitre 1
        Lesson.objects.create(
            unit=unit_fr_a1,
            chapter=chapter_fr_1,
            title_fr="Salutations et politesse",
            title_en="Greetings and politeness",
            description_fr="Les salutations de base et les formules de politesse",
            description_en="Basic greetings and polite expressions",
            lesson_type="vocabulary",
            estimated_duration=15,
            order=1,
            is_published=True
        )

        Lesson.objects.create(
            unit=unit_fr_a1,
            chapter=chapter_fr_1,
            title_fr="Se présenter - nom et âge",
            title_en="Introducing yourself - name and age",
            description_fr="Comment dire son nom et son âge",
            description_en="How to say your name and age",
            lesson_type="vocabulary",
            estimated_duration=12,
            order=2,
            is_published=True
        )

        # Cours 2: Anglais Grammaire (A2)
        unit_en_a2 = Unit.objects.create(
            title_fr="Bases de Grammaire Anglaise",
            title_en="English Grammar Basics",
            description_fr="Maîtrisez les bases de la grammaire anglaise avec des exercices pratiques et des explications claires.",
            description_en="Master the basics of English grammar with practical exercises and clear explanations.",
            level='A2',
            order=2,
            teacher_cms_id=2,
            is_published=True
        )

        # Chapitre 1 du cours d'anglais
        chapter_en_1 = Chapter.objects.create(
            unit=unit_en_a2,
            title_fr="Les temps du présent",
            title_en="Present tenses",
            description_fr="Présent simple et présent continu",
            description_en="Present simple and present continuous",
            theme="grammar",
            order=1,
            style="Open Linguify",
            points_reward=150
        )

        # Leçons du chapitre anglais
        Lesson.objects.create(
            unit=unit_en_a2,
            chapter=chapter_en_1,
            title_fr="Le présent simple",
            title_en="Present simple",
            description_fr="Formation et utilisation du présent simple",
            description_en="Formation and use of present simple",
            lesson_type="grammar",
            estimated_duration=20,
            order=1,
            is_published=True
        )

        # Cours 3: Conversation Française (B1)
        unit_fr_b1 = Unit.objects.create(
            title_fr="Conversation Française Intermédiaire",
            title_en="Intermediate French Conversation",
            description_fr="Développez vos compétences de conversation en français avec des dialogues authentiques et des situations réelles.",
            description_en="Develop your French conversation skills with authentic dialogues and real situations.",
            level='B1',
            order=3,
            teacher_cms_id=1,
            is_published=True
        )

        # Leçon directe (sans chapitre)
        Lesson.objects.create(
            unit=unit_fr_b1,
            title_fr="Au restaurant",
            title_en="At the restaurant",
            description_fr="Commander un repas et interagir avec le serveur",
            description_en="Ordering a meal and interacting with the waiter",
            lesson_type="culture",
            estimated_duration=25,
            order=1,
            is_published=True
        )

        Lesson.objects.create(
            unit=unit_fr_b1,
            title_fr="Demander son chemin",
            title_en="Asking for directions",
            description_fr="Comment demander et donner des directions",
            description_en="How to ask for and give directions",
            lesson_type="vocabulary",
            estimated_duration=18,
            order=2,
            is_published=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Cours créés avec succès:\n'
                f'- {unit_fr_a1.title} (A1) - {unit_fr_a1.lessons.count()} leçons\n'
                f'- {unit_en_a2.title} (A2) - {unit_en_a2.lessons.count()} leçons\n'
                f'- {unit_fr_b1.title} (B1) - {unit_fr_b1.lessons.count()} leçons'
            )
        )

        # Statistiques
        total_units = Unit.objects.count()
        total_chapters = Chapter.objects.count()
        total_lessons = Lesson.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f'\nStatistiques:\n'
                f'- {total_units} unités créées\n'
                f'- {total_chapters} chapitres créés\n'
                f'- {total_lessons} leçons créées'
            )
        )