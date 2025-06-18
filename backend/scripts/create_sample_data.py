#!/usr/bin/env python3
"""
Script pour créer des données de test avec des unités, leçons et vocabulaire
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

def create_sample_unit():
    """Crée une unité de test"""
    with transaction.atomic():
        unit = Unit.objects.create(
            title_en="Family and Relationships",
            title_fr="Famille et Relations",
            title_es="Familia y Relaciones",
            title_nl="Familie en Relaties",
            description_en="Learn about family members and relationships",
            description_fr="Apprenez les membres de la famille et les relations",
            description_es="Aprende sobre los miembros de la familia y las relaciones",
            description_nl="Leer over familieleden en relaties",
            level="A1",
            order=1
        )
        print(f"✅ Unité créée: {unit.title_en} (ID: {unit.id})")
        return unit

def create_sample_lesson(unit):
    """Crée une leçon de test"""
    with transaction.atomic():
        lesson = Lesson.objects.create(
            unit=unit,
            lesson_type="vocabulary",
            title_en="Family Members",
            title_fr="Membres de la Famille",
            title_es="Miembros de la Familia",
            title_nl="Familieleden",
            description_en="Learn the names of family members",
            description_fr="Apprenez les noms des membres de la famille",
            description_es="Aprende los nombres de los miembros de la familia",
            description_nl="Leer de namen van familieleden",
            estimated_duration=30,
            order=1
        )
        print(f"✅ Leçon créée: {lesson.title_en} (ID: {lesson.id})")
        return lesson

def create_sample_content_lesson(lesson):
    """Crée une leçon de contenu de test"""
    with transaction.atomic():
        content_lesson = ContentLesson.objects.create(
            lesson=lesson,
            content_type="VocabularyList",
            title_en="Basic Family Vocabulary",
            title_fr="Vocabulaire de Base de la Famille",
            title_es="Vocabulario Básico de la Familia",
            title_nl="Basis Familie Vocabulaire",
            instruction_en="Learn the names of family members",
            instruction_fr="Apprenez les noms des membres de la famille",
            instruction_es="Aprende los nombres de los miembros de la familia",
            instruction_nl="Leer de namen van familieleden",
            estimated_duration=15,
            order=1
        )
        print(f"✅ Leçon de contenu créée: {content_lesson.title_en} (ID: {content_lesson.id})")
        return content_lesson

def create_sample_vocabulary(content_lesson):
    """Crée du vocabulaire de test"""
    vocabulary_data = [
        {
            "word_en": "mother",
            "word_fr": "mère",
            "word_es": "madre",
            "word_nl": "moeder",
            "definition_en": "Female parent",
            "definition_fr": "Parent de sexe féminin",
            "definition_es": "Progenitora femenina",
            "definition_nl": "Vrouwelijke ouder",
            "word_type_en": "noun",
            "word_type_fr": "nom",
            "word_type_es": "sustantivo",
            "word_type_nl": "zelfstandig naamwoord",
            "example_sentence_en": "My mother is very kind.",
            "example_sentence_fr": "Ma mère est très gentille.",
            "example_sentence_es": "Mi madre es muy amable.",
            "example_sentence_nl": "Mijn moeder is erg aardig."
        },
        {
            "word_en": "father",
            "word_fr": "père",
            "word_es": "padre",
            "word_nl": "vader",
            "definition_en": "Male parent",
            "definition_fr": "Parent de sexe masculin",
            "definition_es": "Progenitor masculino",
            "definition_nl": "Mannelijke ouder",
            "word_type_en": "noun",
            "word_type_fr": "nom",
            "word_type_es": "sustantivo",
            "word_type_nl": "zelfstandig naamwoord",
            "example_sentence_en": "My father works in a bank.",
            "example_sentence_fr": "Mon père travaille dans une banque.",
            "example_sentence_es": "Mi padre trabaja en un banco.",
            "example_sentence_nl": "Mijn vader werkt bij een bank."
        },
        {
            "word_en": "brother",
            "word_fr": "frère",
            "word_es": "hermano",
            "word_nl": "broer",
            "definition_en": "Male sibling",
            "definition_fr": "Frère et sœur masculin",
            "definition_es": "Hermano masculino",
            "definition_nl": "Mannelijke broer of zus",
            "word_type_en": "noun",
            "word_type_fr": "nom",
            "word_type_es": "sustantivo",
            "word_type_nl": "zelfstandig naamwoord",
            "example_sentence_en": "I have one younger brother.",
            "example_sentence_fr": "J'ai un frère plus jeune.",
            "example_sentence_es": "Tengo un hermano menor.",
            "example_sentence_nl": "Ik heb een jongere broer."
        },
        {
            "word_en": "sister",
            "word_fr": "sœur",
            "word_es": "hermana",
            "word_nl": "zus",
            "definition_en": "Female sibling",
            "definition_fr": "Frère et sœur féminin",
            "definition_es": "Hermana femenina",
            "definition_nl": "Vrouwelijke broer of zus",
            "word_type_en": "noun",
            "word_type_fr": "nom",
            "word_type_es": "sustantivo",
            "word_type_nl": "zelfstandig naamwoord",
            "example_sentence_en": "My sister is studying medicine.",
            "example_sentence_fr": "Ma sœur étudie la médecine.",
            "example_sentence_es": "Mi hermana estudia medicina.",
            "example_sentence_nl": "Mijn zus studeert geneeskunde."
        },
        {
            "word_en": "grandmother",
            "word_fr": "grand-mère",
            "word_es": "abuela",
            "word_nl": "grootmoeder",
            "definition_en": "Mother's or father's mother",
            "definition_fr": "Mère de la mère ou du père",
            "definition_es": "Madre de la madre o del padre",
            "definition_nl": "Moeder van moeder of vader",
            "word_type_en": "noun",
            "word_type_fr": "nom",
            "word_type_es": "sustantivo",
            "word_type_nl": "zelfstandig naamwoord",
            "example_sentence_en": "My grandmother makes delicious cookies.",
            "example_sentence_fr": "Ma grand-mère fait de délicieux biscuits.",
            "example_sentence_es": "Mi abuela hace galletas deliciosas.",
            "example_sentence_nl": "Mijn grootmoeder maakt heerlijke koekjes."
        },
        {
            "word_en": "grandfather",
            "word_fr": "grand-père",
            "word_es": "abuelo",
            "word_nl": "grootvader",
            "definition_en": "Mother's or father's father",
            "definition_fr": "Père de la mère ou du père",
            "definition_es": "Padre de la madre o del padre",
            "definition_nl": "Vader van moeder of vader",
            "word_type_en": "noun",
            "word_type_fr": "nom",
            "word_type_es": "sustantivo",
            "word_type_nl": "zelfstandig naamwoord",
            "example_sentence_en": "My grandfather tells great stories.",
            "example_sentence_fr": "Mon grand-père raconte de belles histoires.",
            "example_sentence_es": "Mi abuelo cuenta historias geniales.",
            "example_sentence_nl": "Mijn grootvader vertelt geweldige verhalen."
        },
        {
            "word_en": "son",
            "word_fr": "fils",
            "word_es": "hijo",
            "word_nl": "zoon",
            "definition_en": "Male child",
            "definition_fr": "Enfant de sexe masculin",
            "definition_es": "Hijo varón",
            "definition_nl": "Mannelijk kind",
            "word_type_en": "noun",
            "word_type_fr": "nom",
            "word_type_es": "sustantivo",
            "word_type_nl": "zelfstandig naamwoord",
            "example_sentence_en": "Their son is very talented.",
            "example_sentence_fr": "Leur fils est très talentueux.",
            "example_sentence_es": "Su hijo es muy talentoso.",
            "example_sentence_nl": "Hun zoon is erg getalenteerd."
        },
        {
            "word_en": "daughter",
            "word_fr": "fille",
            "word_es": "hija",
            "word_nl": "dochter",
            "definition_en": "Female child",
            "definition_fr": "Enfant de sexe féminin",
            "definition_es": "Hija mujer",
            "definition_nl": "Vrouwelijk kind",
            "word_type_en": "noun",
            "word_type_fr": "nom",
            "word_type_es": "sustantivo",
            "word_type_nl": "zelfstandig naamwoord",
            "example_sentence_en": "Their daughter loves to read.",
            "example_sentence_fr": "Leur fille aime beaucoup lire.",
            "example_sentence_es": "A su hija le encanta leer.",
            "example_sentence_nl": "Hun dochter houdt van lezen."
        }
    ]
    
    created_count = 0
    with transaction.atomic():
        for vocab_data in vocabulary_data:
            try:
                vocab = VocabularyList.objects.create(
                    content_lesson=content_lesson,
                    **vocab_data
                )
                print(f"✅ Vocabulaire créé: {vocab.word_en} (ID: {vocab.id})")
                created_count += 1
            except Exception as e:
                print(f"❌ Erreur lors de la création de {vocab_data['word_en']}: {e}")
    
    print(f"🎉 {created_count} mots de vocabulaire créés avec succès!")
    return created_count

def main():
    """Fonction principale"""
    print('🎯 CRÉATION DE DONNÉES DE TEST')
    print('=' * 50)
    
    try:
        # Vérification si des données existent déjà
        existing_units = Unit.objects.count()
        if existing_units > 0:
            print(f"⚠️ {existing_units} unités existent déjà.")
            # Auto cleanup for demo purposes
            print("🗑️ Suppression automatique des données existantes...")
            VocabularyList.objects.all().delete()
            ContentLesson.objects.all().delete()
            Lesson.objects.all().delete()
            Unit.objects.all().delete()
            print("✅ Données supprimées")
        
        # Création des données de test
        print("\n📚 Création d'une unité de test...")
        unit = create_sample_unit()
        
        print("\n📖 Création d'une leçon de test...")
        lesson = create_sample_lesson(unit)
        
        print("\n📝 Création d'une leçon de contenu...")
        content_lesson = create_sample_content_lesson(lesson)
        
        print("\n🔤 Création du vocabulaire...")
        vocab_count = create_sample_vocabulary(content_lesson)
        
        print(f"\n🎉 CRÉATION TERMINÉE AVEC SUCCÈS!")
        print(f"   - 1 unité créée")
        print(f"   - 1 leçon créée")
        print(f"   - 1 leçon de contenu créée")
        print(f"   - {vocab_count} mots de vocabulaire créés")
        
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()