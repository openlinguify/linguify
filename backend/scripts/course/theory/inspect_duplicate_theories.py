#!/usr/bin/env python
"""
Script pour inspecter en détail les théories dupliquées
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.course.models import Lesson, ContentLesson, TheoryContent


def main():
    print("=== Inspection détaillée des théories dupliquées ===\n")
    
    # Les 4 leçons avec duplications identifiées
    problem_lessons = [
        (117, "The definite articles"),
        (61, "Plurals"),
        (62, "To have"),
        (122, "Articles (a/an/the)")
    ]
    
    for lesson_id, lesson_name in problem_lessons:
        print(f"\n{'='*50}")
        print(f"Leçon : {lesson_name} (ID: {lesson_id})")
        print(f"{'='*50}")
        
        lesson = Lesson.objects.get(id=lesson_id)
        theories = ContentLesson.objects.filter(
            lesson=lesson,
            content_type='Theory'
        ).order_by('id')
        
        for i, theory in enumerate(theories, 1):
            print(f"\nThéorie #{i}:")
            print(f"  ContentLesson ID: {theory.id}")
            print(f"  Titre EN: '{theory.title_en}'")
            print(f"  Titre FR: '{theory.title_fr}'")
            print(f"  Order: {theory.order}")
            print(f"  Estimated Duration: {theory.estimated_duration}")
            
            if hasattr(theory, 'theory_content'):
                tc = theory.theory_content
                print(f"\n  TheoryContent:")
                print(f"    ID: {tc.id}")
                print(f"    Using JSON Format: {tc.using_json_format}")
                
                if tc.using_json_format:
                    print(f"    Available Languages: {tc.available_languages}")
                    # Afficher un échantillon du contenu
                    if 'en' in tc.language_specific_content:
                        content = tc.language_specific_content['en'].get('content', '')
                        print(f"    EN Content Preview: {content[:100]}...")
                else:
                    # Contenu traditionnel
                    print(f"    EN Content Preview: {tc.content_en[:100] if tc.content_en else 'Empty'}...")
            else:
                print("\n  Pas de TheoryContent associé!")
        
        print(f"\n{'-'*50}")


if __name__ == "__main__":
    main()