# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from django.core.management.base import BaseCommand
from apps.course.models import Unit, Chapter
from django.db.models import Count


class Command(BaseCommand):
    help = 'Compare learning platform structures (Open Linguify vs OpenLinguify)'

    def handle(self, *args, **options):
        self.stdout.write('='*80)
        self.stdout.write('LEARNING PLATFORM STRUCTURE COMPARISON')
        self.stdout.write('='*80)
        
        # Analyze current data
        Open Linguify_chapters = Chapter.objects.filter(style='Open Linguify')
        OpenLinguify_chapters = Chapter.objects.filter(style='OpenLinguify')
        
        self.stdout.write('\n📊 CURRENT DATA ANALYSIS:')
        self.stdout.write('-'*40)
        self.stdout.write(f'Open Linguify-style chapters: {Open Linguify_chapters.count()}')
        self.stdout.write(f'OpenLinguify-style chapters: {OpenLinguify_chapters.count()}')
        
        # Detailed comparison
        self.stdout.write('\n🎯 Open Linguify APPROACH:')
        self.stdout.write('-'*40)
        self.stdout.write('✅ Structured progression: Chapter 1 → Chapter 2 → Chapter 3')
        self.stdout.write('✅ Clear learning path with checkpoints')
        self.stdout.write('✅ Thematic organization (Introductions, Greetings)')
        self.stdout.write('✅ Progress tracking with completion percentages')
        
        for chapter in Open Linguify_chapters:
            self.stdout.write(f'   📘 {chapter.title_en} | Theme: {chapter.theme} | Points: {chapter.points_reward}')
        
        self.stdout.write('\n🎯 OpenLinguify APPROACH:')
        self.stdout.write('-'*40)
        self.stdout.write('✅ Task-based modules: "Décrire une maison"')
        self.stdout.write('✅ Real-world application focus')
        self.stdout.write('✅ Varied activity types: Video, Exercise, Vocabulary, Test')
        self.stdout.write('✅ CECR level progression (A1-, A1, A2, B1, B2, C1)')
        self.stdout.write('✅ Points/Score system with daily challenges')
        
        for chapter in OpenLinguify_chapters:
            self.stdout.write(f'   📙 {chapter.title_fr} | Theme: {chapter.theme} | Points: {chapter.points_reward}')
        
        self.stdout.write('\n🔀 NOTRE IMPLEMENTATION HYBRIDE:')
        self.stdout.write('-'*40)
        self.stdout.write('✅ Support des deux styles dans le même système')
        self.stdout.write('✅ Flexibilité pour différents types de cours')
        self.stdout.write('✅ Système de points unifié')
        self.stdout.write('✅ Progression adaptable (checkpoints optionnels)')
        
        # Recommendations
        self.stdout.write('\n💡 RECOMMENDATIONS:')
        self.stdout.write('-'*40)
        self.stdout.write('1. Utilisez Open Linguify style pour: Cours de grammaire, progressions linéaires')
        self.stdout.write('2. Utilisez OpenLinguify style pour: Modules thématiques, situations pratiques')
        self.stdout.write('3. Combinez les deux pour: Parcours complets et diversifiés')
        
        # Show progression structure
        self.stdout.write('\n📈 STRUCTURE PROGRESSION COMPLETE:')
        self.stdout.write('-'*40)
        
        unit = Unit.objects.first()
        if unit:
            total_points = sum(chapter.points_reward for chapter in unit.chapters.all())
            self.stdout.write(f'Unit: {unit.title_en} (Total: {total_points} points)')
            
            for chapter in unit.chapters.all():
                style_icon = '📘' if chapter.style == 'Open Linguify' else '📙'
                checkpoint = '🔒' if chapter.is_checkpoint_required else '🔓'
                self.stdout.write(f'  {chapter.order:02d}. {style_icon} {chapter.title_fr} {checkpoint} ({chapter.points_reward}pts)')
        
        self.stdout.write('\n' + '='*80)