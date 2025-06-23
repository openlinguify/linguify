# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from django.core.management.base import BaseCommand
from apps.course.models import Unit, Chapter


class Command(BaseCommand):
    help = 'Create OpenLinguify-style sample chapters'

    def handle(self, *args, **options):
        # Get first unit to add chapters to
        unit = Unit.objects.first()
        if not unit:
            self.stdout.write(self.style.ERROR('No units found. Please create a unit first.'))
            return

        # Sample chapters inspired by OpenLinguify structure
        OpenLinguify_chapters = [
            {
                'title_en': 'Describing a House',
                'title_fr': 'Décrire une maison', 
                'title_es': 'Describir una casa',
                'title_nl': 'Een huis beschrijven',
                'theme': 'House description',
                'description_en': 'Learn to describe rooms, furniture and house features',
                'description_fr': 'Apprenez à décrire les pièces, les meubles et les caractéristiques de la maison',
                'description_es': 'Aprende a describir habitaciones, muebles y características de la casa',
                'description_nl': 'Leer kamers, meubels en huiskenmerken te beschrijven',
                'order': 4,
                'style': 'OpenLinguify',
                'is_checkpoint_required': False,
                'points_reward': 150
            },
            {
                'title_en': 'Working at the Office',
                'title_fr': 'Travailler au bureau',
                'title_es': 'Trabajar en la oficina', 
                'title_nl': 'Werken op kantoor',
                'theme': 'Work environment',
                'description_en': 'Professional vocabulary and office situations',
                'description_fr': 'Vocabulaire professionnel et situations de bureau',
                'description_es': 'Vocabulario profesional y situaciones de oficina',
                'description_nl': 'Professionele woordenschat en kantoorsituaties',
                'order': 5,
                'style': 'OpenLinguify',
                'is_checkpoint_required': True,
                'points_reward': 200
            },
            {
                'title_en': 'Shopping for Clothes',
                'title_fr': 'Acheter des vêtements',
                'title_es': 'Comprar ropa',
                'title_nl': 'Kleding kopen',
                'theme': 'Shopping',
                'description_en': 'Learn clothing vocabulary and shopping expressions',
                'description_fr': 'Apprenez le vocabulaire des vêtements et les expressions pour faire du shopping',
                'description_es': 'Aprende vocabulario de ropa y expresiones de compras',
                'description_nl': 'Leer kledingwoordenschat en winkeluitdrukkingen',
                'order': 6,
                'style': 'OpenLinguify',
                'is_checkpoint_required': False,
                'points_reward': 120
            }
        ]

        created_count = 0
        for chapter_data in OpenLinguify_chapters:
            chapter, created = Chapter.objects.get_or_create(
                unit=unit,
                order=chapter_data['order'],
                defaults=chapter_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created OpenLinguify chapter: {chapter.title_fr}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Chapter already exists: {chapter.title_fr}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} OpenLinguify-style chapters')
        )
        
        # Show complete structure with both styles
        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'COMPLETE CHAPTER STRUCTURE - {unit.title_en}')
        self.stdout.write('='*60)
        
        for chapter in unit.chapters.all():
            style_icon = '📘' if chapter.style == 'Open Linguify' else '📙' if chapter.style == 'OpenLinguify' else '📗'
            self.stdout.write(f'  {style_icon} {chapter.title_fr}')
            self.stdout.write(f'     Theme: {chapter.theme}')
            self.stdout.write(f'     Style: {chapter.get_style_display()}')
            self.stdout.write(f'     Points: {chapter.points_reward}')
            self.stdout.write(f'     Progress: {chapter.get_progress_percentage()}%')
            self.stdout.write('')