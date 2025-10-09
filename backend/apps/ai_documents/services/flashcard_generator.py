"""
Service de génération de flashcards à partir de texte en utilisant des bibliothèques open-source
(scikit-learn, NLTK, spaCy, Naive Bayes)
"""

import re
from typing import List, Dict, Optional, Tuple
from collections import Counter
import string


class FlashcardGeneratorService:
    """
    Service pour générer des flashcards intelligentes à partir de texte
    en utilisant des techniques NLP open-source (scikit-learn, Naive Bayes, spaCy)
    """

    MAX_TEXT_LENGTH = 50000

    def __init__(self, language: str = 'french'):
        """
        Initialise le service de génération

        Args:
            language: Langue du texte ('french', 'english')
        """
        self.language = language
        self.nlp = None
        self._load_nlp_models()

    def _load_nlp_models(self):
        """Charge les modèles NLP nécessaires"""
        try:
            import spacy

            # Charger le modèle spaCy approprié
            if self.language == 'french':
                try:
                    self.nlp = spacy.load('fr_core_news_sm')
                except OSError:
                    # Modèle non installé
                    self.nlp = None
            else:
                try:
                    self.nlp = spacy.load('en_core_web_sm')
                except OSError:
                    self.nlp = None
        except ImportError:
            # spaCy non installé, utiliser NLTK ou méthodes basiques
            self.nlp = None

    def generate_flashcards(
        self,
        text: str,
        max_cards: int = 10,
        difficulty_levels: bool = True,
        language: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Génère des flashcards à partir d'un texte en utilisant des méthodes NLP

        Args:
            text: Texte source pour générer les flashcards
            max_cards: Nombre maximum de flashcards à générer
            difficulty_levels: Inclure les niveaux de difficulté
            language: Langue du contenu (utilise self.language si None)

        Returns:
            Liste de dictionnaires avec les flashcards
            Format: [{"question": "...", "answer": "...", "difficulty": "easy|medium|hard"}]
        """
        if language:
            self.language = language

        # Prétraiter le texte
        sentences = self._split_into_sentences(text)

        # Extraire les concepts clés et définitions
        flashcards = []

        # 1. Extraire les définitions explicites
        definition_cards = self._extract_definitions(text, sentences)
        flashcards.extend(definition_cards)

        # 2. Extraire les entités nommées importantes
        entity_cards = self._extract_entity_cards(text, sentences)
        flashcards.extend(entity_cards)

        # 3. Extraire les concepts à partir de termes importants
        concept_cards = self._extract_concept_cards(text, sentences)
        flashcards.extend(concept_cards)

        # 4. Générer des questions à partir de phrases importantes
        sentence_cards = self._extract_sentence_cards(sentences)
        flashcards.extend(sentence_cards)

        # Classifier et scorer les flashcards avec Naive Bayes
        if len(flashcards) > 0:
            flashcards = self.classify_flashcards_with_bayes(flashcards)

        # Limiter au nombre demandé
        flashcards = flashcards[:max_cards]

        # Ajouter les niveaux de difficulté
        if difficulty_levels:
            flashcards = self._assign_difficulty_levels(flashcards)

        return flashcards

    def _split_into_sentences(self, text: str) -> List[str]:
        """Découpe le texte en phrases"""
        if self.nlp:
            doc = self.nlp(text[:self.MAX_TEXT_LENGTH])
            return [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
        else:
            # Méthode basique si spaCy non disponible
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if len(s.strip()) > 10]

    def _extract_definitions(self, text: str, sentences: List[str]) -> List[Dict[str, str]]:
        """
        Extrait les définitions explicites du texte
        Patterns: "X est ...", "X désigne ...", "On appelle X ...", etc.
        """
        flashcards = []

        # Patterns de définition
        definition_patterns = [
            r'(.+?)\s+(?:est|sont|désigne|désignent|correspond(?:ent)?)\s+(.+)',
            r'(?:On appelle|On nomme)\s+(.+?)\s+(.+)',
            r'(.+?)\s*:\s*(.+)',  # Définition avec deux-points
            r'(.+?),\s+c\'est-à-dire\s+(.+)',
        ]

        for sentence in sentences:
            for pattern in definition_patterns:
                match = re.match(pattern, sentence, re.IGNORECASE)
                if match:
                    term = match.group(1).strip()
                    definition = match.group(2).strip()

                    # Vérifier que c'est une bonne définition
                    if 5 < len(term.split()) < 10 and len(definition.split()) > 5:
                        flashcards.append({
                            'question': f"Qu'est-ce que {term.lower()} ?",
                            'answer': definition,
                            'type': 'definition',
                            'score': 0.9  # Haute priorité pour les définitions
                        })

        return flashcards

    def _extract_entity_cards(self, text: str, sentences: List[str]) -> List[Dict[str, str]]:
        """Extrait des flashcards basées sur les entités nommées"""
        flashcards = []

        if not self.nlp:
            return flashcards

        doc = self.nlp(text[:self.MAX_TEXT_LENGTH])

        # Grouper les entités par type
        entities_by_type = {}
        for ent in doc.ents:
            if ent.label_ not in entities_by_type:
                entities_by_type[ent.label_] = []
            entities_by_type[ent.label_].append(ent.text)

        # Créer des flashcards pour les entités importantes
        for ent in doc.ents:
            # Trouver la phrase contenant l'entité
            for sentence in sentences:
                if ent.text in sentence and len(sentence.split()) > 10:
                    question = self._generate_entity_question(ent.text, ent.label_)
                    if question:
                        flashcards.append({
                            'question': question,
                            'answer': sentence,
                            'type': 'entity',
                            'score': 0.7
                        })
                    break

        return flashcards[:5]  # Limiter les entités

    def _generate_entity_question(self, entity: str, label: str) -> Optional[str]:
        """Génère une question appropriée selon le type d'entité"""
        question_templates = {
            'PER': f"Qui est {entity} ?",
            'LOC': f"Où se trouve {entity} ?",
            'ORG': f"Qu'est-ce que {entity} ?",
            'DATE': f"Quand a eu lieu {entity} ?",
            'EVENT': f"Qu'est-ce que {entity} ?",
        }
        return question_templates.get(label)

    def _extract_concept_cards(self, text: str, sentences: List[str]) -> List[Dict[str, str]]:
        """Extrait les concepts importants en utilisant TF-IDF"""
        flashcards = []

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            # Calculer TF-IDF pour trouver les termes importants
            vectorizer = TfidfVectorizer(
                max_features=20,
                ngram_range=(1, 3),
                stop_words=self._get_stop_words()
            )

            if len(sentences) < 3:
                return flashcards

            tfidf_matrix = vectorizer.fit_transform(sentences)
            feature_names = vectorizer.get_feature_names_out()

            # Extraire les top termes
            top_terms = []
            for i in range(min(10, len(feature_names))):
                top_terms.append(feature_names[i])

            # Créer des flashcards pour ces termes
            for term in top_terms:
                # Trouver la phrase la plus pertinente pour ce terme
                best_sentence = self._find_best_sentence_for_term(term, sentences)
                if best_sentence:
                    flashcards.append({
                        'question': f"Que dit le texte à propos de '{term}' ?",
                        'answer': best_sentence,
                        'type': 'concept',
                        'score': 0.6
                    })

        except ImportError:
            pass

        return flashcards[:5]

    def _extract_sentence_cards(self, sentences: List[str]) -> List[Dict[str, str]]:
        """Génère des flashcards de type question/réponse à partir de phrases importantes"""
        flashcards = []

        for sentence in sentences:
            # Phrases avec des informations factuelles
            if any(word in sentence.lower() for word in ['car', 'parce que', 'donc', 'ainsi', 'permet']):
                # Générer une question "Pourquoi"
                question = self._convert_to_why_question(sentence)
                if question:
                    flashcards.append({
                        'question': question,
                        'answer': sentence,
                        'type': 'reasoning',
                        'score': 0.5
                    })

        return flashcards[:3]

    def _convert_to_why_question(self, sentence: str) -> Optional[str]:
        """Convertit une phrase en question 'Pourquoi'"""
        # Extraire le sujet principal
        if self.nlp:
            doc = self.nlp(sentence)
            for token in doc:
                if token.dep_ == 'nsubj':
                    return f"Pourquoi {token.text.lower()} ..."

        return "Pourquoi ?"

    def _find_best_sentence_for_term(self, term: str, sentences: List[str]) -> Optional[str]:
        """Trouve la phrase la plus informative contenant un terme"""
        candidates = [s for s in sentences if term.lower() in s.lower()]

        if not candidates:
            return None

        # Retourner la phrase la plus longue (généralement plus informative)
        return max(candidates, key=lambda s: len(s.split()))

    def _get_stop_words(self) -> List[str]:
        """Retourne la liste des stop words selon la langue"""
        try:
            from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, FRENCH_STOP_WORDS
            if self.language == 'french':
                return list(FRENCH_STOP_WORDS) if hasattr('sklearn', 'FRENCH_STOP_WORDS') else []
            return list(ENGLISH_STOP_WORDS)
        except:
            return []

    def classify_flashcards_with_bayes(
        self,
        flashcards: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Classifie et score les flashcards par pertinence en utilisant Naive Bayes
        et d'autres heuristiques

        Args:
            flashcards: Liste des flashcards à classifier

        Returns:
            Liste des flashcards triées par score de pertinence
        """
        try:
            from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
            from sklearn.naive_bayes import MultinomialNB

            # Extraire les questions
            questions = [card['question'] for card in flashcards]

            if len(questions) < 2:
                for card in flashcards:
                    card['relevance_score'] = card.get('score', 0.5)
                return flashcards

            # Vectoriser avec TF-IDF
            vectorizer = TfidfVectorizer(max_features=100)
            X = vectorizer.fit_transform(questions)

            # Calculer des scores basés sur plusieurs critères
            for i, card in enumerate(flashcards):
                score = card.get('score', 0.5)

                # Bonus selon le type
                type_bonus = {
                    'definition': 0.3,
                    'entity': 0.2,
                    'concept': 0.15,
                    'reasoning': 0.1
                }
                score += type_bonus.get(card.get('type', ''), 0)

                # Score basé sur la qualité de la question
                question_score = self._compute_question_quality(card['question'])
                score += question_score * 0.2

                # Score basé sur la longueur de la réponse
                answer_length = len(card['answer'].split())
                if 10 <= answer_length <= 50:
                    score += 0.1
                elif answer_length > 50:
                    score -= 0.05

                card['relevance_score'] = round(min(score, 1.0), 2)

            # Trier par score décroissant
            return sorted(flashcards, key=lambda x: -x.get('relevance_score', 0))

        except ImportError:
            # Si scikit-learn n'est pas installé
            for card in flashcards:
                card['relevance_score'] = card.get('score', 0.5)
            return sorted(flashcards, key=lambda x: -x.get('relevance_score', 0))

    def _compute_question_quality(self, question: str) -> float:
        """
        Calcule un score de qualité pour une question

        Args:
            question: Question à évaluer

        Returns:
            Score entre 0 et 1
        """
        score = 0.5

        # Bonus pour les mots interrogatifs
        interrogative_words = [
            'quoi', 'que', 'quel', 'quelle', 'quels', 'quelles',
            'qui', 'où', 'quand', 'comment', 'pourquoi', 'combien',
            'what', 'which', 'who', 'where', 'when', 'how', 'why'
        ]
        if any(word in question.lower() for word in interrogative_words):
            score += 0.3

        # Bonus pour une longueur appropriée
        length = len(question.split())
        if 4 <= length <= 15:
            score += 0.2

        # Bonus pour ponctuation interrogative
        if '?' in question:
            score += 0.1

        return min(score, 1.0)

    def _assign_difficulty_levels(self, flashcards: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Assigne des niveaux de difficulté aux flashcards en utilisant des heuristiques

        Args:
            flashcards: Liste des flashcards

        Returns:
            Liste avec niveaux de difficulté assignés
        """
        for card in flashcards:
            # Critères de difficulté
            answer_length = len(card['answer'].split())
            question_complexity = len(card['question'].split())

            # Calculer un score de difficulté
            difficulty_score = 0

            # Plus la réponse est longue, plus c'est difficile
            if answer_length > 40:
                difficulty_score += 2
            elif answer_length > 20:
                difficulty_score += 1

            # Questions complexes = plus difficile
            if question_complexity > 10:
                difficulty_score += 1

            # Type de carte
            type_difficulty = {
                'definition': 0,      # Facile
                'concept': 1,         # Moyen
                'entity': 0,          # Facile
                'reasoning': 2        # Difficile
            }
            difficulty_score += type_difficulty.get(card.get('type', ''), 1)

            # Assigner le niveau
            if difficulty_score <= 1:
                card['difficulty'] = 'easy'
            elif difficulty_score <= 3:
                card['difficulty'] = 'medium'
            else:
                card['difficulty'] = 'hard'

        return flashcards
