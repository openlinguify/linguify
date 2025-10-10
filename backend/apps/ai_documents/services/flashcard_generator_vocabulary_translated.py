"""
Extension du FlashcardGeneratorService pour l'extraction de vocabulaire avec traduction automatique
À intégrer dans flashcard_generator.py
"""

def _generate_vocabulary_with_translation(
    self,
    text: str,
    max_cards: int = 10,
    difficulty_levels: bool = True,
    source_language: Optional[str] = None,
    target_language: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Génère des flashcards en extrayant le vocabulaire d'un texte narratif
    et en le traduisant automatiquement vers une langue cible.

    Exemple: Texte anglais → extrait "medtech startup", "behavioral change", etc.
             → traduit en français → flashcards "medtech startup" → "startup de technologies médicales"

    Args:
        text: Texte narratif source
        max_cards: Nombre maximum de flashcards
        difficulty_levels: Inclure niveaux de difficulté
        source_language: Langue source ('en', 'fr', 'es', etc.)
        target_language: Langue cible pour traduction

    Returns:
        Liste de flashcards avec vocabulaire traduit
    """
    import logging
    from collections import Counter

    logger = logging.getLogger(__name__)

    if not source_language or not target_language:
        logger.error("Source and target languages required for vocabulary_extraction_translated mode")
        return []

    if source_language == target_language:
        logger.warning("Source and target languages are the same, falling back to comprehension mode")
        return self._generate_comprehension_cards(text, max_cards, difficulty_levels)

    # Extraire les termes importants (comme dans _extract_concepts_basic mais plus ciblé)
    flashcards = []

    # Découper en phrases
    sentences = self._split_into_sentences(text)

    if len(sentences) < 2:
        logger.warning("Not enough sentences for vocabulary extraction")
        return []

    # Stop words basiques à ignorer
    stop_words = set([
        # Anglais
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'it', 'its', 'you', 'your', 'we', 'our',
        'they', 'their', 'them', 'who', 'what', 'which', 'when', 'where', 'why',
        # Français
        'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou',
        'mais', 'dans', 'sur', 'avec', 'pour', 'par', 'est', 'sont', 'été',
        'être', 'avoir', 'a', 'ont', 'ce', 'cette', 'ces', 'il', 'elle',
        'nous', 'vous', 'leur', 'leurs', 'qui', 'que', 'quoi', 'où', 'quand'
    ])

    # Compter la fréquence des termes (unigrams, bigrams, trigrams)
    term_freq = Counter()

    for sentence in sentences:
        words = sentence.lower().split()
        words_clean = [w.strip(',.!?;:()[]{}""\'') for w in words]

        for i in range(len(words_clean)):
            word = words_clean[i]

            # Unigrams (mots seuls) - uniquement si >4 lettres et pas stop word
            if len(word) > 4 and word not in stop_words and word.isalpha():
                term_freq[word] += 1

            # Bigrammes (2 mots consécutifs)
            if i < len(words_clean) - 1:
                bigram = f"{words_clean[i]} {words_clean[i+1]}"
                # Au moins un mot non-stop
                if (words_clean[i] not in stop_words or words_clean[i+1] not in stop_words):
                    if len(bigram) > 8:  # Éviter les bigrammes trop courts
                        term_freq[bigram] += 1

            # Trigrammes (3 mots consécutifs) - pour expressions composées
            if i < len(words_clean) - 2:
                trigram = f"{words_clean[i]} {words_clean[i+1]} {words_clean[i+2]}"
                # Au moins 2 mots non-stop
                non_stop_count = sum(1 for w in [words_clean[i], words_clean[i+1], words_clean[i+2]] if w not in stop_words)
                if non_stop_count >= 2 and len(trigram) > 12:
                    term_freq[trigram] += 1

    # Prendre les termes les plus fréquents (max_cards * 1.5 pour avoir de la marge)
    top_terms = [term for term, freq in term_freq.most_common(int(max_cards * 1.5)) if freq >= 2]

    # Prioritiser les termes plus longs (expressions > mots simples)
    top_terms_sorted = sorted(top_terms, key=lambda t: (len(t.split()), term_freq[t]), reverse=True)

    logger.info(f"Extracted {len(top_terms_sorted)} vocabulary terms for translation")

    # Traduire les termes avec le service de traduction
    try:
        from apps.ai_documents.services.translation_service import TranslationService

        translator = TranslationService()

        # Vérifier que l'API est disponible
        if not translator.is_available():
            logger.error("Translation API not available")
            return self._generate_comprehension_cards(text, max_cards, difficulty_levels)

        for term in top_terms_sorted[:max_cards]:
            # Traduire le terme
            translation = translator.translate(term, source_language, target_language)

            if translation and translation != term:
                # Créer la flashcard
                flashcard = {
                    'question': term,
                    'answer': translation,
                    'type': 'vocabulary_translated',
                    'relevance_score': min(term_freq[term] * 0.15, 1.0)  # Score basé sur fréquence
                }

                if difficulty_levels:
                    # Difficulté basée sur longueur et complexité
                    word_count = len(term.split())
                    if word_count == 1:
                        flashcard['difficulty'] = 'easy'
                    elif word_count == 2:
                        flashcard['difficulty'] = 'medium'
                    else:
                        flashcard['difficulty'] = 'hard'

                flashcards.append(flashcard)

                logger.info(f"Translated: '{term}' → '{translation}'")
            else:
                logger.warning(f"Failed to translate or identical: '{term}'")

            if len(flashcards) >= max_cards:
                break

    except ImportError as e:
        logger.error(f"Translation service not available: {str(e)}")
        return self._generate_comprehension_cards(text, max_cards, difficulty_levels)
    except Exception as e:
        logger.error(f"Error during translation: {str(e)}")
        return self._generate_comprehension_cards(text, max_cards, difficulty_levels)

    logger.info(f"Generated {len(flashcards)} vocabulary flashcards with translations")
    return flashcards
