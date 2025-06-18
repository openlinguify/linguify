#!/usr/bin/env python
"""
Script intelligent pour corriger les théories dupliquées en gardant la meilleure version
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.course.models import Lesson, ContentLesson, TheoryContent
from django.db.models import Count, Q


def evaluate_theory_quality(theory):
    """
    Évalue la qualité d'une théorie pour décider laquelle garder
    Score basé sur :
    - Titre informatif (pas juste "Theory")
    - Order approprié
    - Présence du TheoryContent associé
    - Utilisation du format JSON
    - Nombre de langues disponibles
    """
    score = 0
    
    # Titre informatif
    if theory.title_en.lower() != 'theory' and theory.title_en.strip():
        score += 20
    
    # Order approprié (les ordres très élevés comme 100 sont souvent des duplications)
    if 1 <= theory.order <= 10:
        score += 15
    elif theory.order > 100:
        score -= 10
    
    # TheoryContent associé
    if hasattr(theory, 'theory_content'):
        score += 10
        tc = theory.theory_content
        
        # Format JSON préféré
        if tc.using_json_format:
            score += 10
            
        # Plus de langues disponibles
        if hasattr(tc, 'available_languages'):
            score += len(tc.available_languages) * 5
    
    # Les théories récentes sont souvent plus complètes
    if theory.id > 100:  # ID élevé = plus récent
        score += 5
    
    return score


def main():
    print("=== Correction intelligente des théories dupliquées ===\n")
    
    # Trouver les leçons avec plusieurs théories
    lessons_with_multiple_theories = Lesson.objects.annotate(
        theory_count=Count('content_lessons', filter=Q(content_lessons__content_type='Theory'))
    ).filter(theory_count__gt=1)
    
    print(f"Leçons avec duplications : {lessons_with_multiple_theories.count()}\n")
    
    if not lessons_with_multiple_theories.exists():
        print("Aucune duplication trouvée.")
        return
    
    duplicates_to_remove = []
    
    for lesson in lessons_with_multiple_theories:
        print(f"\nLeçon : {lesson.title_en} (ID: {lesson.id})")
        
        theories = ContentLesson.objects.filter(
            lesson=lesson,
            content_type='Theory'
        ).order_by('id')
        
        # Évaluer chaque théorie
        scored_theories = []
        for theory in theories:
            score = evaluate_theory_quality(theory)
            scored_theories.append((theory, score))
            
            print(f"  - ID: {theory.id}, Titre: '{theory.title_en}', Order: {theory.order}, Score: {score}")
            
            if hasattr(theory, 'theory_content'):
                tc = theory.theory_content
                print(f"    TheoryContent: ID {tc.id}, JSON: {tc.using_json_format}")
        
        # Trier par score (meilleur score en premier)
        scored_theories.sort(key=lambda x: x[1], reverse=True)
        
        # Garder la meilleure théorie
        best_theory = scored_theories[0][0]
        print(f"\n  ✓ Meilleure théorie : ID {best_theory.id} (Score: {scored_theories[0][1]})")
        
        # Marquer les autres pour suppression
        for theory, score in scored_theories[1:]:
            print(f"  ✗ À supprimer : ID {theory.id} (Score: {score})")
            duplicates_to_remove.append(theory)
    
    # Demander confirmation
    if duplicates_to_remove:
        print(f"\n{len(duplicates_to_remove)} théories seront supprimées.")
        response = input("Voulez-vous procéder ? (y/n): ")
        
        if response.lower() == 'y':
            for theory in duplicates_to_remove:
                print(f"Suppression de : {theory}")
                theory.delete()
            print("\nToutes les duplications ont été corrigées.")
        else:
            print("\nAucune modification effectuée.")


if __name__ == "__main__":
    main()