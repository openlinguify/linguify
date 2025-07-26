#!/usr/bin/env python3
"""
Script simple pour insérer les cours de test directement en base.
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/mnt/c/Users/louis/WebstormProjects/linguify/backend')

django.setup()

from apps.course.models import Unit
from django.utils import timezone

def insert_test_courses():
    """Insère les cours de test dans la base de données"""
    
    # Données des cours de test
    test_courses = [
        {
            'cms_unit_id': 1,
            'teacher_id': 1,
            'teacher_name': 'Marie Dupont',
            'title_en': 'French for Beginners',
            'title_fr': 'Français pour Débutants',
            'title_es': 'Francés para Principiantes',
            'title_nl': 'Frans voor Beginners',
            'description_en': 'Learn French from scratch with interactive lessons',
            'description_fr': 'Apprenez le français depuis zéro avec des leçons interactives',
            'description_es': 'Aprende francés desde cero con lecciones interactivas',
            'description_nl': 'Leer Frans vanaf nul met interactieve lessen',
            'level': 'A1',
            'order': 1,
            'price': 49.99,
            'is_published': True,
            'is_free': False,
        },
        {
            'cms_unit_id': 2,
            'teacher_id': 1,
            'teacher_name': 'Marie Dupont',
            'title_en': 'Intermediate French Conversation',
            'title_fr': 'Conversation Française Intermédiaire',
            'title_es': 'Conversación Francesa Intermedia',
            'title_nl': 'Tussenliggend Frans Gesprek',
            'description_en': 'Improve your French speaking skills',
            'description_fr': 'Améliorez vos compétences orales en français',
            'description_es': 'Mejora tus habilidades de habla francesa',
            'description_nl': 'Verbeter je Franse sprekvaardigheden',
            'level': 'B1',
            'order': 2,
            'price': 79.99,
            'is_published': True,
            'is_free': False,
        },
        {
            'cms_unit_id': 3,
            'teacher_id': 2,
            'teacher_name': 'John Smith',
            'title_en': 'Free English Grammar Basics',
            'title_fr': 'Bases de Grammaire Anglaise Gratuite',
            'title_es': 'Fundamentos Gratuitos de Gramática Inglesa',
            'title_nl': 'Gratis Engelse Grammatica Basis',
            'description_en': 'Master English grammar with free exercises',
            'description_fr': 'Maîtrisez la grammaire anglaise avec des exercices gratuits',
            'description_es': 'Domina la gramática inglesa con ejercicios gratuitos',
            'description_nl': 'Beheers Engelse grammatica met gratis oefeningen',
            'level': 'A2',
            'order': 1,
            'price': 0.00,
            'is_published': True,
            'is_free': True,
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for course_data in test_courses:
        cms_unit_id = course_data['cms_unit_id']
        
        # Vérifier si le cours existe déjà
        unit, created = Unit.objects.update_or_create(
            cms_unit_id=cms_unit_id,
            defaults={
                **course_data,
                'last_sync': timezone.now()
            }
        )
        
        if created:
            created_count += 1
            print(f"✅ Créé: {unit.title}")
        else:
            updated_count += 1
            print(f"🔄 Mis à jour: {unit.title}")
    
    print(f"\n📊 Résultats:")
    print(f"   ✨ Nouveaux cours: {created_count}")
    print(f"   🔄 Cours mis à jour: {updated_count}")
    print(f"   📈 Total cours CMS: {Unit.objects.filter(cms_unit_id__isnull=False).count()}")
    print(f"   🎯 Total cours publiés: {Unit.objects.filter(is_published=True).count()}")

if __name__ == '__main__':
    insert_test_courses()