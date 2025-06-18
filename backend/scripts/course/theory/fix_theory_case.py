#!/usr/bin/env python
"""
Script pour corriger la casse du content_type des théories
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.course.models import ContentLesson


def main():
    # Compter les théories avec minuscule
    theory_min = ContentLesson.objects.filter(content_type='theory')
    count_min = theory_min.count()
    
    print(f"Nombre de ContentLesson avec content_type='theory' (minuscule): {count_min}")
    
    if count_min > 0:
        print("\nCorrection en cours...")
        
        # Mettre à jour toutes les entrées avec 'theory' vers 'Theory'
        updated = theory_min.update(content_type='Theory')
        
        print(f"Corrigé {updated} entrées de 'theory' vers 'Theory'")
        
        # Vérifier le résultat
        theory_maj_after = ContentLesson.objects.filter(content_type='Theory').count()
        theory_min_after = ContentLesson.objects.filter(content_type='theory').count()
        
        print(f"\nAprès correction:")
        print(f"ContentLessons avec 'Theory' (majuscule): {theory_maj_after}")
        print(f"ContentLessons avec 'theory' (minuscule): {theory_min_after}")
    else:
        print("Aucune correction nécessaire - toutes les théories ont déjà la bonne casse")


if __name__ == "__main__":
    main()