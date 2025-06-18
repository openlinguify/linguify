#!/usr/bin/env python3
"""
Script de démonstration du système de vocabulaire Linguify
Montre comment utiliser les différents scripts et fonctionnalités
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Use SQLite for testing
os.environ['EMAIL_DEBUG'] = 'True'
os.environ['TEST_MODE'] = 'True'

django.setup()

from apps.course.models import Unit, Lesson, ContentLesson, VocabularyList
from django.db import transaction

def demo_add_vocabulary_programmatically():
    """Démontre comment ajouter du vocabulaire directement via le code"""
    print("\n🔧 DÉMONSTRATION: Ajout de vocabulaire via code Python")
    print("=" * 60)
    
    # Récupérer la leçon de contenu existante
    try:
        content_lesson = ContentLesson.objects.get(title_en="Basic Family Vocabulary")
        print(f"✅ Leçon de contenu trouvée: {content_lesson.title_en}")
    except ContentLesson.DoesNotExist:
        print("❌ Aucune leçon de contenu trouvée")
        return
    
    # Nouveau vocabulaire à ajouter
    new_vocabulary = [
        {
            "word_en": "cousin",
            "word_fr": "cousin",
            "word_es": "primo",
            "word_nl": "neef",
            "definition_en": "Child of one's aunt or uncle",
            "definition_fr": "Enfant de la tante ou de l'oncle",
            "definition_es": "Hijo de la tía o del tío",
            "definition_nl": "Kind van tante of oom",
            "word_type_en": "noun",
            "word_type_fr": "nom",
            "word_type_es": "sustantivo",
            "word_type_nl": "zelfstandig naamwoord",
            "example_sentence_en": "My cousin lives in Paris.",
            "example_sentence_fr": "Mon cousin habite à Paris.",
            "example_sentence_es": "Mi primo vive en París.",
            "example_sentence_nl": "Mijn neef woont in Parijs."
        },
        {
            "word_en": "aunt",
            "word_fr": "tante",
            "word_es": "tía",
            "word_nl": "tante",
            "definition_en": "Sister of one's parent",
            "definition_fr": "Sœur du parent",
            "definition_es": "Hermana del padre o madre",
            "definition_nl": "Zuster van ouder",
            "word_type_en": "noun",
            "word_type_fr": "nom",
            "word_type_es": "sustantivo",
            "word_type_nl": "zelfstandig naamwoord",
            "example_sentence_en": "My aunt is a teacher.",
            "example_sentence_fr": "Ma tante est professeure.",
            "example_sentence_es": "Mi tía es profesora.",
            "example_sentence_nl": "Mijn tante is lerares."
        }
    ]
    
    print(f"\n📝 Ajout de {len(new_vocabulary)} nouveaux mots...")
    with transaction.atomic():
        for vocab_data in new_vocabulary:
            try:
                vocab = VocabularyList.objects.create(
                    content_lesson=content_lesson,
                    **vocab_data
                )
                print(f"✅ Ajouté: {vocab.word_en} -> {vocab.word_fr}")
            except Exception as e:
                print(f"❌ Erreur pour {vocab_data['word_en']}: {e}")
    
    # Vérification du total
    total_vocab = content_lesson.vocabulary_lists.count()
    print(f"\n📊 Total de vocabulaire dans la leçon: {total_vocab} mots")

def demo_query_vocabulary():
    """Démontre comment interroger le vocabulaire"""
    print("\n🔍 DÉMONSTRATION: Interrogation du vocabulaire")
    print("=" * 60)
    
    # Trouver tout le vocabulaire commençant par une certaine lettre
    print("1. Mots commençant par 'f' en anglais:")
    f_words = VocabularyList.objects.filter(word_en__istartswith='f')
    for word in f_words:
        print(f"   • {word.word_en} ({word.word_fr})")
    
    # Trouver par type de mot
    print("\n2. Tous les noms (nouns):")
    nouns = VocabularyList.objects.filter(word_type_en='noun')[:5]  # Limiter à 5
    for noun in nouns:
        print(f"   • {noun.word_en} - {noun.definition_en[:30]}...")
    
    # Recherche dans les définitions
    print("\n3. Mots avec 'parent' dans la définition:")
    parent_words = VocabularyList.objects.filter(definition_en__icontains='parent')
    for word in parent_words:
        print(f"   • {word.word_en}: {word.definition_en}")
    
    # Statistiques par langue
    print("\n4. Statistiques:")
    total_words = VocabularyList.objects.count()
    unique_en_words = VocabularyList.objects.values('word_en').distinct().count()
    print(f"   • Total de mots: {total_words}")
    print(f"   • Mots anglais uniques: {unique_en_words}")

def demo_vocabulary_methods():
    """Démontre les méthodes disponibles sur les objets vocabulaire"""
    print("\n⚙️ DÉMONSTRATION: Méthodes des objets vocabulaire")
    print("=" * 60)
    
    # Prendre un mot comme exemple
    try:
        word = VocabularyList.objects.get(word_en='mother')
        print(f"🔤 Mot d'exemple: {word.word_en}")
        
        # Tester les méthodes de traduction
        print("\n1. Méthodes de traduction:")
        for lang in ['fr', 'es', 'nl']:
            translation = word.get_translation(lang)
            definition = word.get_definition(lang)
            print(f"   • {lang.upper()}: {translation} - {definition[:40]}...")
        
        # Tester les phrases d'exemple
        print("\n2. Phrases d'exemple:")
        for lang in ['en', 'fr', 'es', 'nl']:
            example = word.get_example_sentence(lang)
            if example:
                print(f"   • {lang.upper()}: {example}")
        
        # Tester les types de mots
        print("\n3. Types de mots:")
        for lang in ['en', 'fr', 'es', 'nl']:
            word_type = word.get_word_type(lang)
            print(f"   • {lang.upper()}: {word_type}")
            
    except VocabularyList.DoesNotExist:
        print("❌ Mot 'mother' non trouvé")

def demo_lesson_structure():
    """Démontre la structure hiérarchique des leçons"""
    print("\n🏗️ DÉMONSTRATION: Structure des leçons")
    print("=" * 60)
    
    # Parcourir la hiérarchie
    for unit in Unit.objects.all():
        print(f"📚 Unité: {unit.title_en} ({unit.level})")
        
        for lesson in unit.lessons.all():
            print(f"  📖 Leçon: {lesson.title_en} ({lesson.lesson_type})")
            
            for content_lesson in lesson.content_lessons.all():
                vocab_count = content_lesson.vocabulary_lists.count()
                print(f"    📝 Contenu: {content_lesson.title_en} ({content_lesson.content_type})")
                print(f"        🔤 {vocab_count} mots de vocabulaire")
                
                # Afficher quelques mots
                if vocab_count > 0:
                    sample_words = content_lesson.vocabulary_lists.all()[:3]
                    for word in sample_words:
                        print(f"          • {word.word_en} / {word.word_fr}")

def demo_bulk_operations():
    """Démontre les opérations en lot"""
    print("\n📦 DÉMONSTRATION: Opérations en lot")
    print("=" * 60)
    
    # Compter par type de mot
    print("1. Distribution par type de mot (EN):")
    word_types = VocabularyList.objects.values('word_type_en').distinct()
    for word_type in word_types:
        count = VocabularyList.objects.filter(word_type_en=word_type['word_type_en']).count()
        print(f"   • {word_type['word_type_en']}: {count} mots")
    
    # Mise à jour en lot (exemple: ajouter un synonyme)
    print("\n2. Exemple de mise à jour en lot:")
    mother_words = VocabularyList.objects.filter(word_en='mother')
    if mother_words.exists():
        mother = mother_words.first()
        if not mother.synonymous_en:
            mother.synonymous_en = "mom, mama"
            mother.synonymous_fr = "maman"
            mother.synonymous_es = "mamá"
            mother.synonymous_nl = "mama"
            mother.save()
            print("   ✅ Synonymes ajoutés pour 'mother'")
        else:
            print("   ℹ️ Synonymes déjà présents pour 'mother'")
    
    # Recherche avancée
    print("\n3. Recherche avancée:")
    # Mots qui ont des exemples de phrases
    words_with_examples = VocabularyList.objects.exclude(example_sentence_en__isnull=True).exclude(example_sentence_en__exact='')
    print(f"   • Mots avec exemples: {words_with_examples.count()}")
    
    # Mots qui ont des synonymes
    words_with_synonyms = VocabularyList.objects.exclude(synonymous_en__isnull=True).exclude(synonymous_en__exact='')
    print(f"   • Mots avec synonymes: {words_with_synonyms.count()}")

def main():
    """Fonction principale de démonstration"""
    print('🎯 DÉMONSTRATION DU SYSTÈME DE VOCABULAIRE LINGUIFY')
    print('=' * 70)
    print('Ce script démontre les fonctionnalités du système de vocabulaire')
    print('=' * 70)
    
    try:
        # Vérifier qu'il y a des données
        if VocabularyList.objects.count() == 0:
            print("⚠️ Aucun vocabulaire trouvé. Exécutez d'abord create_sample_data.py")
            return
        
        # Lancer les démonstrations
        demo_lesson_structure()
        demo_query_vocabulary()
        demo_vocabulary_methods()
        demo_add_vocabulary_programmatically()
        demo_bulk_operations()
        
        print("\n🎉 DÉMONSTRATION TERMINÉE!")
        print("\n📋 RÉSUMÉ DES FONCTIONNALITÉS DISPONIBLES:")
        print("   1. ✅ Connexion à la base de données PostgreSQL/SQLite")
        print("   2. ✅ Modèles multilingues (EN, FR, ES, NL)")
        print("   3. ✅ Structure hiérarchique (Unit -> Lesson -> ContentLesson -> Vocabulary)")
        print("   4. ✅ Méthodes de traduction et d'accès aux données")
        print("   5. ✅ Scripts d'ajout interactif et automatique")
        print("   6. ✅ Opérations de recherche et de filtrage")
        print("   7. ✅ Gestion des synonymes, exemples et types de mots")
        
        print("\n🚀 PROCHAINES ÉTAPES SUGGÉRÉES:")
        print("   • Utiliser fill_vocabulary_interactive.py pour ajouter du vocabulaire")
        print("   • Intégrer avec PostgreSQL en production")
        print("   • Créer des APIs REST pour le frontend")
        print("   • Ajouter des exercices de vocabulaire")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()