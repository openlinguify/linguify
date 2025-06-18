#!/usr/bin/env python
"""
Script pour diagnostiquer les problèmes de création de théorie
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


def main():
    # 1. Vérifier toutes les valeurs content_type existantes
    print("=== Valeurs uniques de content_type ===")
    content_types = ContentLesson.objects.values_list('content_type', flat=True).distinct()
    type_counts = {}
    for ct in content_types:
        count = ContentLesson.objects.filter(content_type=ct).count()
        type_counts[ct] = count
    
    # Afficher les types sans duplications
    for ct, count in sorted(type_counts.items()):
        print(f"  {ct}: {count} entrées")
    
    print("\n=== Leçons spécifiques ===")
    # 2. Vérifier quelques leçons spécifiques
    test_lessons = ['Basic Adjectives', 'Articles (a/an/the)', 'Possessive Adjectives']
    
    for lesson_title in test_lessons:
        print(f"\n--- {lesson_title} ---")
        lesson = Lesson.objects.filter(title_en=lesson_title).first()
        
        if lesson:
            print(f"Lesson ID: {lesson.id}")
            
            # Tous les ContentLesson pour cette leçon
            all_content = ContentLesson.objects.filter(lesson=lesson)
            print(f"Total ContentLessons: {all_content.count()}")
            
            for content in all_content:
                print(f"  ID: {content.id}, Type: '{content.content_type}', Title: {content.title_en}")
                
                # Vérifier TheoryContent
                if hasattr(content, 'theory_content'):
                    theory = content.theory_content
                    print(f"    TheoryContent ID: {theory.id}, Using JSON: {theory.using_json_format}")
            
            # Chercher spécifiquement Theory (avec majuscule)
            theory_maj = ContentLesson.objects.filter(lesson=lesson, content_type='Theory')
            print(f"ContentLessons avec type 'Theory' (majuscule): {theory_maj.count()}")
            
            # Chercher theory (minuscule)
            theory_min = ContentLesson.objects.filter(lesson=lesson, content_type='theory')
            print(f"ContentLessons avec type 'theory' (minuscule): {theory_min.count()}")
            
        else:
            print(f"Leçon non trouvée")
    
    # 3. Statistiques globales
    print("\n=== Statistiques globales ===")
    total_lessons = Lesson.objects.count()
    lessons_with_theory_maj = Lesson.objects.filter(content_lessons__content_type='Theory').distinct().count()
    lessons_with_theory_min = Lesson.objects.filter(content_lessons__content_type='theory').distinct().count()
    
    print(f"Total leçons: {total_lessons}")
    print(f"Leçons avec 'Theory' (majuscule): {lessons_with_theory_maj}")
    print(f"Leçons avec 'theory' (minuscule): {lessons_with_theory_min}")
    
    # 4. Vérifier les dernières créations
    print("\n=== Dernières ContentLessons créées ===")
    recent = ContentLesson.objects.filter(content_type__icontains='theory').order_by('-id')[:10]
    for content in recent:
        print(f"ID: {content.id}, Type: '{content.content_type}', Lesson: {content.lesson.title_en}")


if __name__ == "__main__":
    main()