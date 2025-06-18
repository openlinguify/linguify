#!/usr/bin/env python
"""
Script pour générer un rapport détaillé sur le contenu théorique
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

from apps.course.models import Lesson, ContentLesson, TheoryContent, Unit
from django.db.models import Count, Q


def main():
    print("=== RAPPORT DÉTAILLÉ DU CONTENU THÉORIQUE ===\n")
    
    # Statistiques globales
    total_lessons = Lesson.objects.count()
    lessons_with_theory = Lesson.objects.filter(
        content_lessons__content_type='Theory'
    ).distinct().count()
    
    total_theories = ContentLesson.objects.filter(content_type='Theory').count()
    
    print(f"Statistiques globales :")
    print(f"- Total de leçons : {total_lessons}")
    print(f"- Leçons avec théorie : {lessons_with_theory}")
    print(f"- Total de théories : {total_theories}")
    print(f"- Couverture : {lessons_with_theory/total_lessons*100:.1f}%")
    
    # Par unité
    print("\n=== Analyse par unité ===")
    units = Unit.objects.all().order_by('order')
    
    for unit in units:
        lessons_in_unit = Lesson.objects.filter(unit=unit)
        lessons_with_theory_in_unit = lessons_in_unit.filter(
            content_lessons__content_type='Theory'
        ).distinct()
        
        print(f"\nUnité {unit.order}: {unit.title_en}")
        print(f"  Leçons : {lessons_in_unit.count()}")
        print(f"  Avec théorie : {lessons_with_theory_in_unit.count()}")
        if lessons_in_unit.count() > 0:
            print(f"  Couverture : {lessons_with_theory_in_unit.count()/lessons_in_unit.count()*100:.1f}%")
        else:
            print(f"  Couverture : N/A (aucune leçon)")
        
        # Leçons sans théorie dans cette unité
        lessons_without_theory = lessons_in_unit.exclude(
            content_lessons__content_type='Theory'
        )
        
        if lessons_without_theory.exists():
            print(f"  Leçons sans théorie :")
            for lesson in lessons_without_theory:
                print(f"    - {lesson.title_en}")
    
    # Duplications
    print("\n=== Analyse des duplications ===")
    lessons_with_duplicates = Lesson.objects.annotate(
        theory_count=Count('content_lessons', filter=Q(content_lessons__content_type='Theory'))
    ).filter(theory_count__gt=1)
    
    if lessons_with_duplicates.exists():
        print(f"Leçons avec théories dupliquées : {lessons_with_duplicates.count()}")
        for lesson in lessons_with_duplicates:
            print(f"  - {lesson.title_en} : {lesson.theory_count} théories")
    else:
        print("Aucune duplication trouvée")
    
    # Théories orphelines
    print("\n=== Théories orphelines ===")
    orphan_theories = TheoryContent.objects.filter(content_lesson__isnull=True)
    print(f"Théories sans ContentLesson : {orphan_theories.count()}")
    
    # Format JSON vs traditionnel
    print("\n=== Formats utilisés ===")
    json_theories = TheoryContent.objects.filter(using_json_format=True).count()
    traditional_theories = TheoryContent.objects.filter(using_json_format=False).count()
    
    print(f"Format JSON : {json_theories}")
    print(f"Format traditionnel : {traditional_theories}")
    
    # Recommandations
    print("\n=== RECOMMANDATIONS ===")
    
    if lessons_without_theory.count() > 0:
        print("1. Des leçons n'ont pas de théorie. Utilisez :")
        print("   python manage.py analyze_missing_theory --create")
    
    if lessons_with_duplicates.exists():
        print("2. Des duplications ont été trouvées. Utilisez :")
        print("   python scripts/find_duplicate_theories.py")
    
    if orphan_theories.exists():
        print("3. Des théories orphelines existent. Vérifiez manuellement.")
    
    print("\n4. Pour une analyse détaillée :")
    print("   python scripts/debug_theory_creation.py")


if __name__ == "__main__":
    main()