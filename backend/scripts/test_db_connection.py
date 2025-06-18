#!/usr/bin/env python3
"""
Script simple pour tester la connexion à la base de données
et afficher les statistiques du vocabulaire
"""

import os
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Set environment to use SQLite for testing
os.environ['EMAIL_DEBUG'] = 'True'
os.environ['TEST_MODE'] = 'True'

import django
django.setup()

from django.db import connection
from apps.course.models import Unit, Lesson, ContentLesson, VocabularyList

def test_connection():
    """Test la connexion à la base de données"""
    print('=== Test de connexion à la base de données ===')
    try:
        with connection.cursor() as cursor:
            # Different query based on database type
            db_vendor = connection.vendor
            if db_vendor == 'postgresql':
                cursor.execute('SELECT version()')
                version = cursor.fetchone()
                print(f'✅ Connexion PostgreSQL réussie!')
                print(f'Version: {version[0][:50]}...')
            elif db_vendor == 'sqlite':
                cursor.execute('SELECT sqlite_version()')
                version = cursor.fetchone()
                print(f'✅ Connexion SQLite réussie!')
                print(f'Version: {version[0]}')
            else:
                cursor.execute('SELECT 1')
                print(f'✅ Connexion {db_vendor} réussie!')
            return True
    except Exception as e:
        print(f'❌ Erreur de connexion: {e}')
        return False

def show_statistics():
    """Affiche les statistiques des données"""
    print('\n=== Statistiques des données existantes ===')
    try:
        units_count = Unit.objects.count()
        lessons_count = Lesson.objects.count()
        content_lessons_count = ContentLesson.objects.count()
        vocab_count = VocabularyList.objects.count()
        
        print(f'📚 Units: {units_count}')
        print(f'📖 Lessons: {lessons_count}')
        print(f'📝 ContentLessons: {content_lessons_count}')
        print(f'🔤 VocabularyList: {vocab_count}')
        
        return True
    except Exception as e:
        print(f'❌ Erreur lors de la récupération des statistiques: {e}')
        return False

def show_vocabulary_samples():
    """Affiche des exemples de vocabulaire"""
    print('\n=== Exemples de vocabulaire existant ===')
    try:
        vocab_sample = VocabularyList.objects.all()[:5]
        if vocab_sample:
            for vocab in vocab_sample:
                print(f'ID: {vocab.id} | EN: {vocab.word_en} | FR: {vocab.word_fr} | ES: {vocab.word_es} | NL: {vocab.word_nl}')
        else:
            print('Aucun vocabulaire trouvé dans la base de données')
        return True
    except Exception as e:
        print(f'❌ Erreur lors de la récupération du vocabulaire: {e}')
        return False

def show_lessons_vocabulary_distribution():
    """Affiche la répartition du vocabulaire par leçon"""
    print('\n=== Répartition du vocabulaire par leçon ===')
    try:
        for lesson in Lesson.objects.all()[:10]:  # Limiter à 10 pour l'affichage
            vocab_count = VocabularyList.objects.filter(content_lesson__lesson=lesson).count()
            print(f'Lesson {lesson.id} - "{lesson.title_en}": {vocab_count} mots')
        return True
    except Exception as e:
        print(f'❌ Erreur lors de la récupération de la distribution: {e}')
        return False

def show_content_lessons_vocabulary():
    """Affiche le vocabulaire par leçon de contenu"""
    print('\n=== Vocabulaire par leçon de contenu ===')
    try:
        content_lessons_with_vocab = ContentLesson.objects.filter(
            content_type__icontains='vocabulary'
        )[:5]  # Limiter à 5
        
        for content_lesson in content_lessons_with_vocab:
            vocab_count = content_lesson.vocabulary_lists.count()
            print(f'ContentLesson {content_lesson.id} - "{content_lesson.title_en}" ({content_lesson.content_type}): {vocab_count} mots')
            
            # Afficher quelques mots de vocabulaire de cette leçon
            vocab_items = content_lesson.vocabulary_lists.all()[:3]
            for vocab in vocab_items:
                print(f'  • {vocab.word_en} / {vocab.word_fr}')
                
        return True
    except Exception as e:
        print(f'❌ Erreur lors de la récupération du vocabulaire par leçon: {e}')
        return False

def main():
    """Fonction principale"""
    print('🎯 TEST DE CONNEXION ET STATISTIQUES VOCABULAIRE')
    print('=' * 60)
    
    # Test de connexion
    if not test_connection():
        print('❌ Impossible de continuer sans connexion à la base de données')
        sys.exit(1)
    
    # Statistiques générales
    if not show_statistics():
        print('⚠️ Problème avec les statistiques')
    
    # Exemples de vocabulaire
    if not show_vocabulary_samples():
        print('⚠️ Problème avec les exemples de vocabulaire')
    
    # Distribution par leçon
    if not show_lessons_vocabulary_distribution():
        print('⚠️ Problème avec la distribution par leçon')
    
    # Vocabulaire par leçon de contenu
    if not show_content_lessons_vocabulary():
        print('⚠️ Problème avec le vocabulaire par leçon de contenu')
    
    print('\n✅ Test terminé avec succès!')

if __name__ == "__main__":
    main()