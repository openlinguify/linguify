#!/usr/bin/env python
"""
Script pour trouver et corriger les théories dupliquées
"""
import os
import sys
import django

# Configuration Django
# Remonter jusqu'au répertoire backend
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.course.models import Lesson, ContentLesson, TheoryContent
from django.db.models import Count


def main():
    print("=== Recherche des théories dupliquées ===\n")
    
    # Trouver les leçons avec plusieurs théories
    lessons_with_multiple_theories = Lesson.objects.annotate(
        theory_count=Count('content_lessons', filter=models.Q(content_lessons__content_type='Theory'))
    ).filter(theory_count__gt=1)
    
    print(f"Nombre de leçons avec plusieurs théories : {lessons_with_multiple_theories.count()}\n")
    
    for lesson in lessons_with_multiple_theories:
        print(f"Leçon : {lesson.title_en} (ID: {lesson.id})")
        print(f"  Nombre de théories : {lesson.theory_count}")
        
        theories = ContentLesson.objects.filter(
            lesson=lesson,
            content_type='Theory'
        ).order_by('id')
        
        for theory in theories:
            print(f"  - ID: {theory.id}, Titre: {theory.title_en}, Order: {theory.order}")
            if hasattr(theory, 'theory_content'):
                tc = theory.theory_content
                print(f"    TheoryContent ID: {tc.id}, JSON: {tc.using_json_format}")
                if tc.using_json_format:
                    langs = ', '.join(tc.available_languages)
                    print(f"    Langues disponibles: {langs}")
            else:
                print(f"    Pas de TheoryContent associé!")
        
        print()
    
    # Optionnel : Proposer une correction
    if lessons_with_multiple_theories.exists():
        response = input("\nVoulez-vous supprimer les théories dupliquées (garder seulement la première) ? (y/n): ")
        
        if response.lower() == 'y':
            for lesson in lessons_with_multiple_theories:
                theories = ContentLesson.objects.filter(
                    lesson=lesson,
                    content_type='Theory'
                ).order_by('id')
                
                # Garder la première théorie
                first_theory = theories.first()
                duplicates = theories[1:]
                
                for duplicate in duplicates:
                    print(f"Suppression de : {duplicate}")
                    duplicate.delete()
            
            print("\nToutes les duplications ont été supprimées.")
        else:
            print("\nAucune modification effectuée.")
    
    # Vérification finale
    print("\n=== Vérification finale ===")
    final_lessons_with_multiple = Lesson.objects.annotate(
        theory_count=Count('content_lessons', filter=models.Q(content_lessons__content_type='Theory'))
    ).filter(theory_count__gt=1).count()
    
    print(f"Leçons avec plusieurs théories après correction : {final_lessons_with_multiple}")


if __name__ == "__main__":
    import django.db.models as models
    main()