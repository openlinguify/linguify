# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from django.core.management.base import BaseCommand
from apps.course.models import Unit, Chapter


class Command(BaseCommand):
    help = 'Create sample chapters inspired by Open Linguify structure'

    def handle(self, *args, **options):
        # Get first unit to add chapters to
        unit = Unit.objects.first()
        if not unit:
            self.stdout.write(self.style.ERROR('No units found. Please create a unit first.'))
            return

        # Sample chapters inspired by Open Linguify's A1 course structure
        sample_chapters = [
            {
                'title_en': 'Chapter 1: Introductions',
                'title_fr': 'Chapitre 1 : Présentations', 
                'title_es': 'Capítulo 1: Presentaciones',
                'title_nl': 'Hoofdstuk 1: Introducties',
                'theme': 'Introductions',
                'description_en': 'Learn to introduce yourself and meet new people',
                'description_fr': 'Apprenez à vous présenter et à rencontrer de nouvelles personnes',
                'description_es': 'Aprende a presentarte y conocer gente nueva',
                'description_nl': 'Leer jezelf voor te stellen en nieuwe mensen te ontmoeten',
                'order': 1,
                'is_checkpoint_required': True
            },
            {
                'title_en': 'Chapter 2: Greetings & Politeness',
                'title_fr': 'Chapitre 2 : Salutations et politesse',
                'title_es': 'Capítulo 2: Saludos y cortesía',
                'title_nl': 'Hoofdstuk 2: Begroetingen en beleefdheid',
                'theme': 'Greetings',
                'description_en': 'Master common greetings and polite expressions',
                'description_fr': 'Maîtrisez les salutations courantes et les expressions polies',
                'description_es': 'Domina los saludos comunes y las expresiones corteses',
                'description_nl': 'Beheers veelvoorkomende begroetingen en beleefde uitdrukkingen',
                'order': 2,
                'is_checkpoint_required': True
            },
            {
                'title_en': 'Chapter 3: Numbers & Time',
                'title_fr': 'Chapitre 3 : Nombres et temps',
                'title_es': 'Capítulo 3: Números y tiempo',
                'title_nl': 'Hoofdstuk 3: Getallen en tijd',
                'theme': 'Numbers',
                'description_en': 'Learn numbers, dates, and time expressions',
                'description_fr': 'Apprenez les nombres, les dates et les expressions de temps',
                'description_es': 'Aprende números, fechas y expresiones de tiempo',
                'description_nl': 'Leer getallen, data en tijdsuitdrukkingen',
                'order': 3,
                'is_checkpoint_required': False
            }
        ]

        created_count = 0
        for chapter_data in sample_chapters:
            chapter, created = Chapter.objects.get_or_create(
                unit=unit,
                order=chapter_data['order'],
                defaults=chapter_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created chapter: {chapter.title_en}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Chapter already exists: {chapter.title_en}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample chapters for unit "{unit.title_en}"')
        )
        
        # Show structure
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'UNIT: {unit.title_en}')
        self.stdout.write('='*50)
        
        for chapter in unit.chapters.all():
            self.stdout.write(f'  📖 {chapter.title_en}')
            self.stdout.write(f'     Theme: {chapter.theme}')
            self.stdout.write(f'     Progress: {chapter.get_progress_percentage()}%')
            self.stdout.write(f'     Checkpoint required: {chapter.is_checkpoint_required}')
            self.stdout.write('')