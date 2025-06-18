#!/usr/bin/env python
"""
Script pour prévisualiser ce que les commandes de création de théorie vont faire
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.course.models import Lesson, ContentLesson, TheoryContent
from apps.course.management.commands.create_smart_theory_lesson import Command as SmartCommand


def preview_theory_creation(lesson_id):
    """Prévisualise ce qui sera créé pour une leçon"""
    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except Lesson.DoesNotExist:
        print(f"❌ Lesson ID {lesson_id} n'existe pas")
        return
    
    cmd = SmartCommand()
    
    # Extraire le titre
    title = cmd.extract_smart_title(lesson)
    
    # Détecter le template
    template = cmd.detect_template_from_context(lesson, title)
    
    # Vérifier si une théorie existe déjà
    existing = ContentLesson.objects.filter(
        lesson=lesson,
        content_type='Theory'
    ).first()
    
    print(f"\n📚 PREVIEW pour Lesson ID {lesson_id}")
    print(f"=" * 50)
    print(f"Lesson: {lesson.title_en}")
    print(f"Unit: {lesson.unit.title if lesson.unit else 'N/A'}")
    print(f"Titre détecté: {title}")
    print(f"Template qui sera utilisé: {template}")
    
    if existing:
        print(f"\n⚠️  ATTENTION: Une théorie existe déjà!")
        print(f"   Content ID: {existing.id}")
        print(f"   Order: {existing.order}")
        if hasattr(existing, 'theory_content'):
            theory = existing.theory_content
            if theory.using_json_format:
                print(f"   Format: JSON")
                print(f"   Langues: {', '.join(theory.get_available_languages())}")
            else:
                print(f"   Format: Standard")
    else:
        print(f"\n✅ Aucune théorie existante, création possible")
    
    # Prévisualiser le contenu du template
    print(f"\n📄 Contenu du template '{template}':")
    print("-" * 30)
    
    # Essayer de charger le template
    template_path = f'/mnt/c/Users/louis/WebstormProjects/linguify/backend/apps/course/templates/json/{template}_theory.json'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            import json
            content = json.load(f)
            for lang, data in content.items():
                print(f"\n{lang.upper()}:")
                print(f"  Content: {data.get('content', '')[:100]}...")
                if 'explanation' in data:
                    print(f"  Explanation: {data['explanation'][:100]}...")
    else:
        print(f"Template {template} non trouvé")


def list_lessons_without_theory(unit_id=None):
    """Liste toutes les leçons sans théorie"""
    query = Lesson.objects.all()
    if unit_id:
        query = query.filter(unit_id=unit_id)
    
    lessons_without_theory = []
    
    for lesson in query:
        has_theory = ContentLesson.objects.filter(
            lesson=lesson,
            content_type='Theory'
        ).exists()
        
        if not has_theory:
            lessons_without_theory.append(lesson)
    
    print(f"\n📋 Leçons sans théorie:")
    print("=" * 50)
    
    for lesson in lessons_without_theory:
        cmd = SmartCommand()
        title = cmd.extract_smart_title(lesson)
        template = cmd.detect_template_from_context(lesson, title)
        
        print(f"\nLesson ID {lesson.id}: {lesson.title_en}")
        print(f"  Unit: {lesson.unit.title if lesson.unit else 'N/A'}")
        print(f"  Titre détecté: {title}")
        print(f"  Template: {template}")
    
    print(f"\n\nTotal: {len(lessons_without_theory)} leçons sans théorie")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Prévisualiser la création de théorie')
    parser.add_argument('--lesson-id', type=int, help='ID de la leçon à prévisualiser')
    parser.add_argument('--list-missing', action='store_true', help='Lister les leçons sans théorie')
    parser.add_argument('--unit', type=int, help='Filtrer par unité')
    
    args = parser.parse_args()
    
    if args.lesson_id:
        preview_theory_creation(args.lesson_id)
    elif args.list_missing:
        list_lessons_without_theory(args.unit)
    else:
        parser.print_help()