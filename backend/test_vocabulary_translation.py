"""
Test script pour verifier l'extraction de vocabulaire avec traduction automatique
"""
import os
import sys
import django

# Force UTF-8 encoding for output (Windows compatibility)
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.ai_documents.services.flashcard_generator import FlashcardGeneratorService
from apps.ai_documents.services.translation_service import TranslationService

# Texte test (extrait d'une description de poste en anglais - plus long pour extraction)
test_text = """
We're looking for a talented professional to join our medtech startup focused on behavioral change.
The medtech startup is growing rapidly in the healthcare sector.
Our medtech startup needs someone with experience in behavioral change programs.

The ideal candidate will have experience with strategic partnerships and healthcare innovation.
Strategic partnerships are essential for our growth strategy.
We value healthcare innovation and digital transformation.

You will work with cutting-edge technology to develop digital therapeutics.
Digital therapeutics are revolutionizing patient care.
Our digital therapeutics platform uses evidence-based approaches.

The position involves patient outcomes analysis and quality improvement.
Patient outcomes are our primary focus and key success metric.
We measure patient outcomes through rigorous clinical trials.

Healthcare innovation drives everything we do at our company.
Join our team to advance healthcare innovation through technology.
"""

def test_translation_service():
    """Test du service de traduction"""
    print("=" * 80)
    print("TEST 1: Service de traduction LibreTranslate")
    print("=" * 80)

    translator = TranslationService()

    # Vérifier disponibilité
    print("\n1. Vérification de la disponibilité de l'API...")
    is_available = translator.is_available()
    print(f"   API disponible: {is_available}")

    if not is_available:
        print("   WARNING: L'API de traduction n'est pas disponible.")
        print("   Causes possibles:")
        print("   - Pas de connexion Internet")
        print("   - L'instance publique est surchargee")
        print("   - Firewall/proxy bloque l'acces")
        return False

    # Test de traduction simple
    print("\n2. Test de traduction EN -> FR...")
    test_terms = [
        "medtech startup",
        "behavioral change",
        "strategic partnerships",
        "healthcare innovation",
        "digital therapeutics"
    ]

    for term in test_terms:
        translation = translator.translate(term, "en", "fr")
        print(f"   '{term}' -> '{translation}'")

    return True


def test_vocabulary_extraction():
    """Test de l'extraction de vocabulaire avec traduction"""
    print("\n" + "=" * 80)
    print("TEST 2: Extraction de vocabulaire avec traduction")
    print("=" * 80)

    generator = FlashcardGeneratorService(language='english')

    print("\n1. Génération de flashcards en mode 'vocabulary_extraction_translated'...")
    print(f"   Texte source (EN): {len(test_text)} caractères")
    print(f"   Langue cible: FR")

    flashcards = generator.generate_flashcards(
        text=test_text,
        max_cards=8,
        difficulty_levels=True,
        language='en',
        mode='vocabulary_extraction_translated',
        source_language='en',
        target_language='fr'
    )

    print(f"\n2. Résultats: {len(flashcards)} flashcards générées\n")

    for i, card in enumerate(flashcards, 1):
        print(f"   Flashcard #{i}")
        print(f"   |-- Front (EN): {card['question']}")
        print(f"   |-- Back (FR):  {card['answer']}")
        print(f"   |-- Difficulte: {card.get('difficulty', 'N/A')}")
        print(f"   |-- Score:      {card.get('relevance_score', 'N/A')}")
        print()

    return len(flashcards) > 0


def test_deck_language_detection():
    """Test de la logique de détection dans document_import_views"""
    print("\n" + "=" * 80)
    print("TEST 3: Logique de détection de langue du deck")
    print("=" * 80)

    # Simuler la logique de document_import_views.py
    test_cases = [
        {
            'name': 'Deck bilingue EN→FR',
            'deck_front_lang': 'en',
            'deck_back_lang': 'fr',
            'generation_mode': 'auto',
            'expected_mode': 'vocabulary_extraction_translated'
        },
        {
            'name': 'Deck monolingue FR→FR',
            'deck_front_lang': 'fr',
            'deck_back_lang': 'fr',
            'generation_mode': 'auto',
            'expected_mode': 'auto'  # Pas de traduction
        },
        {
            'name': 'Deck bilingue ES→EN',
            'deck_front_lang': 'es',
            'deck_back_lang': 'en',
            'generation_mode': 'comprehension',
            'expected_mode': 'vocabulary_extraction_translated'
        },
        {
            'name': 'Mode vocabulary_pairs explicite',
            'deck_front_lang': 'en',
            'deck_back_lang': 'fr',
            'generation_mode': 'vocabulary_pairs',
            'expected_mode': 'vocabulary_pairs'  # Pas de surcharge
        }
    ]

    for case in test_cases:
        print(f"\n   Test: {case['name']}")
        print(f"   |-- Front language: {case['deck_front_lang']}")
        print(f"   |-- Back language:  {case['deck_back_lang']}")
        print(f"   |-- Mode initial:   {case['generation_mode']}")

        # Logique de document_import_views.py
        deck_front_lang = case['deck_front_lang']
        deck_back_lang = case['deck_back_lang']
        generation_mode = case['generation_mode']

        needs_translation = (
            deck_front_lang and deck_back_lang and
            deck_front_lang != deck_back_lang and
            generation_mode in ['auto', 'comprehension']
        )

        if needs_translation:
            generation_mode = 'vocabulary_extraction_translated'

        result = "PASS" if generation_mode == case['expected_mode'] else "FAIL"
        print(f"   |-- Mode final:     {generation_mode} [{result}]")


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("TEST DE L'EXTRACTION DE VOCABULAIRE AVEC TRADUCTION AUTOMATIQUE")
    print("=" * 80)

    # Test 1: Service de traduction
    translation_ok = test_translation_service()

    if translation_ok:
        # Test 2: Extraction de vocabulaire
        extraction_ok = test_vocabulary_extraction()

        # Test 3: Logique de détection
        test_deck_language_detection()

        print("\n" + "=" * 80)
        print("TOUS LES TESTS SONT TERMINÉS")
        print("=" * 80)
    else:
        print("\n[WARNING] Les tests d'extraction ne peuvent pas etre executes car l'API de traduction n'est pas disponible.")
        print("   Vous pouvez:")
        print("   1. Vérifier votre connexion Internet")
        print("   2. Réessayer plus tard (l'instance publique peut être surchargée)")
        print("   3. Configurer votre propre instance LibreTranslate avec Docker:")
        print("      docker run -ti --rm -p 5000:5000 libretranslate/libretranslate")
