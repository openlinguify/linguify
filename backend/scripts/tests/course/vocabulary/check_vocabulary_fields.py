#!/usr/bin/env python3
"""
Script pour vérifier que tous les champs du modèle VocabularyList sont correctement remplis
"""

import os
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ['EMAIL_DEBUG'] = 'True'
os.environ['TEST_MODE'] = 'True'

import django
django.setup()

from apps.course.models import VocabularyList

def check_vocabulary_fields():
    """Vérifie tous les champs d'un mot de vocabulaire"""
    print('🔍 VÉRIFICATION COMPLÈTE DES CHAMPS VOCABULAIRE')
    print('=' * 60)

    # Prendre un exemple de mot
    try:
        word = VocabularyList.objects.get(word_en='mother')
        print(f'📝 Mot d\'exemple: {word.word_en}')
        print()
        
        # Vérifier tous les champs obligatoires
        print('🌍 TRADUCTIONS (obligatoires):')
        print(f'  EN: {word.word_en}')
        print(f'  FR: {word.word_fr}')
        print(f'  ES: {word.word_es}')
        print(f'  NL: {word.word_nl}')
        
        print()
        print('📖 DÉFINITIONS (obligatoires):')
        print(f'  EN: {word.definition_en}')
        print(f'  FR: {word.definition_fr}')
        print(f'  ES: {word.definition_es}')
        print(f'  NL: {word.definition_nl}')
        
        print()
        print('🏷️ TYPES DE MOTS (obligatoires):')
        print(f'  EN: {word.word_type_en}')
        print(f'  FR: {word.word_type_fr}')
        print(f'  ES: {word.word_type_es}')
        print(f'  NL: {word.word_type_nl}')
        
        print()
        print('💬 EXEMPLES DE PHRASES (optionnels):')
        print(f'  EN: {word.example_sentence_en or "[Non défini]"}')
        print(f'  FR: {word.example_sentence_fr or "[Non défini]"}')
        print(f'  ES: {word.example_sentence_es or "[Non défini]"}')
        print(f'  NL: {word.example_sentence_nl or "[Non défini]"}')
        
        print()
        print('🔄 SYNONYMES (optionnels):')
        print(f'  EN: {word.synonymous_en or "[Non défini]"}')
        print(f'  FR: {word.synonymous_fr or "[Non défini]"}')
        print(f'  ES: {word.synonymous_es or "[Non défini]"}')
        print(f'  NL: {word.synonymous_nl or "[Non défini]"}')
        
        print()
        print('↔️ ANTONYMES (optionnels):')
        print(f'  EN: {word.antonymous_en or "[Non défini]"}')
        print(f'  FR: {word.antonymous_fr or "[Non défini]"}')
        print(f'  ES: {word.antonymous_es or "[Non défini]"}')
        print(f'  NL: {word.antonymous_nl or "[Non défini]"}')
        
        print()
        print('🔗 AUTRES INFOS:')
        print(f'  ID: {word.id}')
        print(f'  ContentLesson: {word.content_lesson.title_en}')
        
        return True
        
    except VocabularyList.DoesNotExist:
        print('❌ Mot "mother" non trouvé')
        return False
    except Exception as e:
        print(f'❌ Erreur: {e}')
        return False

def test_vocabulary_methods():
    """Teste les méthodes du modèle"""
    print('\n⚙️ TEST DES MÉTHODES DU MODÈLE')
    print('=' * 40)
    
    try:
        word = VocabularyList.objects.get(word_en='mother')
        
        # Tester les méthodes get_*
        print('📝 Test des méthodes getter:')
        for lang in ['fr', 'es', 'nl']:
            translation = word.get_translation(lang)
            definition = word.get_definition(lang)
            word_type = word.get_word_type(lang)
            example = word.get_example_sentence(lang)
            synonyms = word.get_synonymous(lang)
            antonyms = word.get_antonymous(lang)
            
            print(f'  {lang.upper()}: {translation} ({word_type})')
            print(f'       Def: {definition[:50]}...')
            if example:
                print(f'       Ex: {example[:50]}...')
            if synonyms:
                print(f'       Syn: {synonyms}')
            if antonyms:
                print(f'       Ant: {antonyms}')
            print()
            
        return True
    except Exception as e:
        print(f'❌ Erreur lors du test des méthodes: {e}')
        return False

def check_all_vocabulary_completeness():
    """Vérifie la complétude de tous les mots de vocabulaire"""
    print('\n📊 ANALYSE DE COMPLÉTUDE DE TOUT LE VOCABULAIRE')
    print('=' * 50)
    
    total_words = VocabularyList.objects.count()
    print(f'📈 Total de mots: {total_words}')
    
    # Compter les champs vides par type
    stats = {
        'Traductions complètes': 0,
        'Définitions complètes': 0,
        'Types de mots complets': 0,
        'Avec exemples': 0,
        'Avec synonymes': 0,
        'Avec antonymes': 0
    }
    
    for word in VocabularyList.objects.all():
        # Traductions (obligatoires)
        if all([word.word_en, word.word_fr, word.word_es, word.word_nl]):
            stats['Traductions complètes'] += 1
            
        # Définitions (obligatoires)
        if all([word.definition_en, word.definition_fr, word.definition_es, word.definition_nl]):
            stats['Définitions complètes'] += 1
            
        # Types de mots (obligatoires)
        if all([word.word_type_en, word.word_type_fr, word.word_type_es, word.word_type_nl]):
            stats['Types de mots complets'] += 1
            
        # Exemples (optionnels)
        if any([word.example_sentence_en, word.example_sentence_fr, word.example_sentence_es, word.example_sentence_nl]):
            stats['Avec exemples'] += 1
            
        # Synonymes (optionnels)
        if any([word.synonymous_en, word.synonymous_fr, word.synonymous_es, word.synonymous_nl]):
            stats['Avec synonymes'] += 1
            
        # Antonymes (optionnels)
        if any([word.antonymous_en, word.antonymous_fr, word.antonymous_es, word.antonymous_nl]):
            stats['Avec antonymes'] += 1
    
    print()
    for stat_name, count in stats.items():
        percentage = (count / total_words * 100) if total_words > 0 else 0
        print(f'✅ {stat_name}: {count}/{total_words} ({percentage:.1f}%)')

def main():
    """Fonction principale"""
    print('🎯 VÉRIFICATION DES CHAMPS VOCABULAIRE')
    print('=' * 50)
    
    # Test 1: Vérifier un mot spécifique
    if not check_vocabulary_fields():
        print('⚠️ Impossible de continuer sans données')
        return
    
    # Test 2: Tester les méthodes
    test_vocabulary_methods()
    
    # Test 3: Analyser la complétude globale
    check_all_vocabulary_completeness()
    
    print('\n🎉 VÉRIFICATION TERMINÉE!')

if __name__ == "__main__":
    main()