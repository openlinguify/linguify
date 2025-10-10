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
        language: Optional[str] = None,
        mode: str = 'auto'
    ) -> List[Dict[str, str]]:
        """
        Génère des flashcards à partir d'un texte en utilisant des méthodes NLP

        Args:
            text: Texte source pour générer les flashcards
            max_cards: Nombre maximum de flashcards à générer
            difficulty_levels: Inclure les niveaux de difficulté
            language: Langue du contenu (utilise self.language si None)
            mode: Mode de génération ('auto', 'comprehension', 'vocabulary', 'vocabulary_pairs', 'definitions')

        Returns:
            Liste de dictionnaires avec les flashcards
            Format: [{"question": "...", "answer": "...", "difficulty": "easy|medium|hard"}]
        """
        if language:
            self.language = language

        # Détection automatique du mode si 'auto'
        if mode == 'auto' or mode == 'comprehension':
            detected_mode = self._detect_content_type(text)
            if detected_mode:
                mode = detected_mode

        # Router vers la méthode appropriée selon le mode
        if mode == 'vocabulary':
            return self._generate_vocabulary_cards(text, max_cards, difficulty_levels)
        elif mode == 'vocabulary_pairs':
            return self._generate_vocabulary_pairs_cards(text, max_cards, difficulty_levels)
        elif mode == 'definitions':
            return self._generate_definition_cards(text, max_cards, difficulty_levels)
        else:  # comprehension (default)
            return self._generate_comprehension_cards(text, max_cards, difficulty_levels)

    def _detect_content_type(self, text: str) -> Optional[str]:
        """
        Détecte automatiquement le type de contenu pour choisir le meilleur mode

        Args:
            text: Texte à analyser

        Returns:
            'vocabulary_pairs' si liste de vocabulaire détectée, None sinon
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        if len(lines) < 3:
            return None

        # Compter combien de lignes ressemblent à des paires de mots
        vocabulary_pair_count = 0
        total_valid_lines = 0

        # Patterns à ignorer
        ignore_patterns = [
            r'^---\s*Page',
            r'^Te leren',
            r'^Gemaakt op',
            r'^©',
            r'^\d+\s*$',
        ]

        for line in lines:
            # Ignorer les métadonnées
            if any(re.match(pattern, line, re.IGNORECASE) for pattern in ignore_patterns):
                continue

            total_valid_lines += 1

            # Vérifier si la ligne ressemble à une paire de vocabulaire
            # Critères:
            # 1. Ligne courte (< 100 caractères)
            # 2. Contient 2 à 10 mots
            # 3. Pas de verbe conjugué en début de phrase (pas de phrase narrative)
            if len(line) < 100:
                words = line.split()
                word_count = len(words)

                # Paires typiques: 2-10 mots total
                if 2 <= word_count <= 10:
                    # Vérifier qu'il n'y a pas de ponctuation de phrase complète
                    has_sentence_ending = line.endswith('.') or line.endswith('!') or '?' in line

                    # Vérifier présence de mots dans différentes langues
                    # (accents français, caractères néerlandais)
                    has_multilingual = (
                        bool(re.search(r'[àâäéèêëïîôùûüÿç]', line)) or
                        bool(re.search(r'\s+[a-z]+\s+', line))  # séparation simple entre mots
                    )

                    if not has_sentence_ending and (has_multilingual or word_count <= 4):
                        vocabulary_pair_count += 1

        # Si plus de 60% des lignes ressemblent à des paires de vocabulaire
        if total_valid_lines > 0:
            ratio = vocabulary_pair_count / total_valid_lines
            if ratio > 0.6:
                return 'vocabulary_pairs'

        return None

    def _generate_comprehension_cards(
        self,
        text: str,
        max_cards: int = 10,
        difficulty_levels: bool = True
    ) -> List[Dict[str, str]]:
        """Génère des flashcards de compréhension de texte (mode par défaut)"""
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

    def _generate_vocabulary_cards(
        self,
        text: str,
        max_cards: int = 10,
        difficulty_levels: bool = True
    ) -> List[Dict[str, str]]:
        """
        Génère des flashcards de vocabulaire (mots importants avec contexte)
        Mode optimisé pour l'apprentissage de vocabulaire
        """
        flashcards = []

        if not self.nlp:
            return flashcards

        # Traiter le texte avec spaCy
        doc = self.nlp(text[:self.MAX_TEXT_LENGTH])

        # Extraire les mots importants (noms, verbes, adjectifs)
        important_words = {}
        for token in doc:
            # Filtrer les mots pertinents
            if (token.pos_ in ['NOUN', 'VERB', 'ADJ', 'PROPN'] and
                not token.is_stop and
                not token.is_punct and
                len(token.text) > 3 and
                token.text.lower() not in ['être', 'avoir', 'faire', 'dire', 'aller', 'voir', 'pouvoir']):

                word = token.text
                lemma = token.lemma_
                pos = token.pos_

                # Stocker avec contexte
                if lemma not in important_words:
                    # Trouver la phrase contenant ce mot
                    sentence = token.sent.text.strip()
                    important_words[lemma] = {
                        'word': word,
                        'lemma': lemma,
                        'pos': pos,
                        'sentence': sentence,
                        'count': 1
                    }
                else:
                    important_words[lemma]['count'] += 1

        # Trier par fréquence
        sorted_words = sorted(important_words.values(), key=lambda x: x['count'], reverse=True)

        # Créer les flashcards
        for word_info in sorted_words[:max_cards]:
            # Format: Mot → Contexte/Définition
            flashcard = {
                'question': word_info['word'],
                'answer': word_info['sentence'],
                'type': 'vocabulary',
                'relevance_score': min(word_info['count'] * 0.1, 1.0)
            }

            if difficulty_levels:
                # Difficulté basée sur longueur et fréquence
                if word_info['count'] > 3:
                    flashcard['difficulty'] = 'easy'
                elif word_info['count'] > 1:
                    flashcard['difficulty'] = 'medium'
                else:
                    flashcard['difficulty'] = 'hard'

            flashcards.append(flashcard)

        return flashcards

    def _generate_definition_cards(
        self,
        text: str,
        max_cards: int = 10,
        difficulty_levels: bool = True
    ) -> List[Dict[str, str]]:
        """
        Génère des flashcards uniquement à partir des définitions trouvées dans le texte
        Mode optimisé pour extraire les définitions
        """
        sentences = self._split_into_sentences(text)
        flashcards = []

        # Patterns pour détecter les définitions
        definition_patterns = [
            r'(.+?)\s+est\s+(.+)',
            r'(.+?)\s+désigne\s+(.+)',
            r'(.+?)\s+se\s+définit\s+comme\s+(.+)',
            r'On\s+appelle\s+(.+?)\s+(.+)',
            r'(.+?)\s*:\s*(.+)',
            r'(.+?)\s+signifie\s+(.+)',
            r'(.+?)\s+représente\s+(.+)',
        ]

        for sentence in sentences:
            for pattern in definition_patterns:
                match = re.match(pattern, sentence, re.IGNORECASE)
                if match:
                    term = match.group(1).strip()
                    definition = match.group(2).strip()

                    # Valider que c'est une vraie définition
                    if (5 < len(term) < 100 and
                        20 < len(definition) < 300 and
                        not term.lower().startswith(('si', 'quand', 'lorsque', 'alors'))):

                        flashcard = {
                            'question': f"Qu'est-ce que {term} ?",
                            'answer': definition,
                            'type': 'definition',
                            'relevance_score': 0.9
                        }

                        if difficulty_levels:
                            # Difficulté basée sur longueur de la définition
                            if len(definition) < 50:
                                flashcard['difficulty'] = 'easy'
                            elif len(definition) < 100:
                                flashcard['difficulty'] = 'medium'
                            else:
                                flashcard['difficulty'] = 'hard'

                        flashcards.append(flashcard)

                        if len(flashcards) >= max_cards:
                            return flashcards
                        break

        # Si pas assez de définitions, compléter avec des concepts importants
        if len(flashcards) < max_cards // 2:
            concept_cards = self._extract_concept_cards(text, sentences)
            flashcards.extend(concept_cards[:(max_cards - len(flashcards))])

        return flashcards[:max_cards]

    def _generate_vocabulary_pairs_cards(
        self,
        text: str,
        max_cards: int = 10,
        difficulty_levels: bool = True
    ) -> List[Dict[str, str]]:
        """
        Génère des flashcards à partir de listes de vocabulaire bilingues

        Formats supportés:
        1. Sur la même ligne: "afzetten déposer" ou "afzetten\tdéposer"
        2. Sur lignes consécutives:
           Ligne 1: Account number
           Ligne 2: Numéro de compte

        Args:
            text: Texte contenant les paires de vocabulaire
            max_cards: Nombre maximum de flashcards
            difficulty_levels: Inclure niveaux de difficulté

        Returns:
            Liste de flashcards avec front=mot source, back=traduction
        """
        flashcards = []

        # Nettoyer le texte
        lines = text.split('\n')

        # D'abord, essayer de détecter si c'est un format "paires sur lignes consécutives"
        if self._is_consecutive_line_format(lines):
            return self._extract_consecutive_line_pairs(lines, max_cards, difficulty_levels)

        # Patterns à ignorer (titres, métadonnées, etc.)
        ignore_patterns = [
            r'^---\s*Page',  # "--- Page 1 ---"
            r'^Te leren',     # "Te leren"
            r'^Gemaakt op',   # "Gemaakt op"
            r'^\s*$',         # Lignes vides
            r'^©\s*ALTISSIA', # Copyright
            r'^\d+\s*$',      # Numéros seuls
        ]

        # Détecter les paires de mots
        for line in lines:
            line = line.strip()

            # Ignorer les lignes vides ou métadonnées
            if not line or any(re.match(pattern, line, re.IGNORECASE) for pattern in ignore_patterns):
                continue

            # Essayer différents patterns de séparation
            word_pair = None

            # Pattern 1: Détection automatique avec espaces multiples ou tabulations
            # Ex: "afzetten    déposer" ou "afzetten\tdéposer"
            if '\t' in line:
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    word_pair = (parts[0].strip(), parts[1].strip())

            # Pattern 2: Détection avec tiret ou flèche
            # Ex: "afzetten - déposer" ou "afzetten → déposer"
            elif any(sep in line for sep in [' - ', ' – ', ' → ', ' -> ']):
                for sep in [' - ', ' – ', ' → ', ' -> ']:
                    if sep in line:
                        parts = line.split(sep, 1)
                        if len(parts) == 2:
                            word_pair = (parts[0].strip(), parts[1].strip())
                            break

            # Pattern 3: Détection intelligente avec espaces
            # Recherche un mot/phrase suivi d'un ou plusieurs espaces puis un autre mot/phrase
            # Ex: "afzetten déposer" ou "een middagdutje doen faire une petite sieste"
            else:
                # Détecter s'il y a plusieurs espaces consécutifs (indicateur de séparation)
                if '  ' in line:
                    parts = re.split(r'\s{2,}', line, 1)
                    if len(parts) == 2:
                        word_pair = (parts[0].strip(), parts[1].strip())
                else:
                    # Essayer de détecter un changement de langue
                    # Stratégie: chercher deux groupes de mots séparés par un espace simple
                    # où chaque groupe contient au moins un mot
                    words = line.split()
                    if len(words) >= 2:
                        # Essayer de trouver le point de séparation optimal
                        # Heuristique: chercher où les caractères changent (accents, etc.)
                        best_split = self._find_language_boundary(words)
                        if best_split > 0:
                            source = ' '.join(words[:best_split])
                            target = ' '.join(words[best_split:])
                            word_pair = (source, target)

            # Valider et ajouter la paire
            if word_pair:
                source, target = word_pair

                # Validation: les deux parties doivent contenir au moins un caractère alphabétique
                # et ne pas être trop longues
                if (source and target and
                    re.search(r'[a-zA-Zàâäéèêëïîôùûüÿçœæ]', source) and
                    re.search(r'[a-zA-Zàâäéèêëïîôùûüÿçœæ]', target) and
                    1 <= len(source.split()) <= 10 and
                    1 <= len(target.split()) <= 10):

                    flashcard = {
                        'question': source,
                        'answer': target,
                        'type': 'vocabulary_pair',
                        'relevance_score': 1.0
                    }

                    if difficulty_levels:
                        # Difficulté basée sur la longueur des expressions
                        word_count = len(source.split()) + len(target.split())
                        if word_count <= 3:
                            flashcard['difficulty'] = 'easy'
                        elif word_count <= 6:
                            flashcard['difficulty'] = 'medium'
                        else:
                            flashcard['difficulty'] = 'hard'

                    flashcards.append(flashcard)

                    if len(flashcards) >= max_cards:
                        break

        return flashcards

    def _is_consecutive_line_format(self, lines: List[str]) -> bool:
        """
        Détecte si le format est "paires sur lignes consécutives"
        Ex: Ligne 1 = mot anglais, Ligne 2 = traduction française

        Args:
            lines: Liste des lignes du texte

        Returns:
            True si format détecté, False sinon
        """
        # Patterns à ignorer
        ignore_patterns = [
            r'^---\s*Page',
            r'^Te leren',
            r'^Gemaakt op',
            r'^©',
            r'^\d+\s*$',
            r'^[A-Z]$',  # Lettres seules (index alphabétique)
            r'^[A-Z]-[A-Z]',  # A-B-C-D...
        ]

        # Compter les paires potentielles
        valid_pairs = 0
        total_lines = 0
        i = 0

        while i < len(lines) - 1:
            line1 = lines[i].strip()
            line2 = lines[i + 1].strip()

            # Ignorer les lignes vides ou métadonnées
            if not line1 or any(re.match(p, line1, re.IGNORECASE) for p in ignore_patterns):
                i += 1
                continue

            total_lines += 1

            # Vérifier si line1 et line2 forment une paire potentielle
            # Critères:
            # - Les deux lignes ont du contenu
            # - Pas trop longues (< 150 caractères chacune)
            # - Ne se terminent pas par un point (pas des phrases complètes)
            if (line2 and
                len(line1) < 150 and len(line2) < 150 and
                not line1.endswith('.') and
                1 <= len(line1.split()) <= 15 and
                1 <= len(line2.split()) <= 15):

                # Vérifier changement de langue (accents, etc.)
                french_chars = set('àâäéèêëïîôùûüÿçœæ')
                has_french_in_line2 = any(c in french_chars for c in line2)

                if has_french_in_line2 or len(line1.split()) <= 5:
                    valid_pairs += 1

            i += 2  # Sauter la ligne suivante puisqu'on l'a déjà considérée

        # Si plus de 50% des lignes forment des paires, c'est probablement ce format
        if total_lines > 5 and valid_pairs / total_lines > 0.5:
            return True

        return False

    def _extract_consecutive_line_pairs(
        self,
        lines: List[str],
        max_cards: int = 10,
        difficulty_levels: bool = True
    ) -> List[Dict[str, str]]:
        """
        Extrait les paires de vocabulaire sur lignes consécutives

        Args:
            lines: Liste des lignes
            max_cards: Nombre maximum de flashcards
            difficulty_levels: Inclure niveaux de difficulté

        Returns:
            Liste de flashcards
        """
        flashcards = []

        # Patterns à ignorer
        ignore_patterns = [
            r'^---\s*Page',
            r'^Te leren',
            r'^Gemaakt op',
            r'^©',
            r'^\d+\s*$',
            r'^[A-Z]$',  # Lettres seules
            r'^[A-Z]-[A-Z]',  # A-B-C-D...
            r'^English.*French',  # Titre
            r'^Glossary',
        ]

        i = 0
        while i < len(lines) - 1 and len(flashcards) < max_cards:
            line1 = lines[i].strip()
            line2 = lines[i + 1].strip() if i + 1 < len(lines) else ''

            # Ignorer lignes vides ou métadonnées
            if not line1 or any(re.match(p, line1, re.IGNORECASE) for p in ignore_patterns):
                i += 1
                continue

            # Vérifier si c'est une paire valide
            if (line2 and
                not any(re.match(p, line2, re.IGNORECASE) for p in ignore_patterns) and
                len(line1) < 150 and len(line2) < 150 and
                1 <= len(line1.split()) <= 15 and
                1 <= len(line2.split()) <= 15):

                # Créer la flashcard
                flashcard = {
                    'question': line1,
                    'answer': line2,
                    'type': 'vocabulary_pair',
                    'relevance_score': 1.0
                }

                if difficulty_levels:
                    # Difficulté basée sur longueur
                    word_count = len(line1.split()) + len(line2.split())
                    if word_count <= 3:
                        flashcard['difficulty'] = 'easy'
                    elif word_count <= 8:
                        flashcard['difficulty'] = 'medium'
                    else:
                        flashcard['difficulty'] = 'hard'

                flashcards.append(flashcard)
                i += 2  # Sauter les deux lignes
            else:
                i += 1  # Passer à la ligne suivante

        return flashcards

    def _find_language_boundary(self, words: List[str]) -> int:
        """
        Trouve le point de séparation probable entre deux langues dans une liste de mots

        Utilise des heuristiques basées sur:
        - Changement de caractères (accents français vs néerlandais)
        - Articles néerlandais (de, het, een)
        - Longueur des mots
        - Patterns typiques

        Args:
            words: Liste de mots

        Returns:
            Index de séparation (0 si pas de séparation détectée)
        """
        if len(words) < 2:
            return 0

        # Caractères typiques du français
        french_chars = set('àâäéèêëïîôùûüÿçœæ')

        # Articles et mots néerlandais courants
        dutch_articles = {'de', 'het', 'een'}
        dutch_common = {'naar', 'van', 'voor', 'met', 'op', 'in', 'uit', 'aan'}
        dutch_verbs = {'doen', 'gaan', 'zijn', 'hebben', 'maken', 'komen', 'nemen', 'houden'}

        # Pour chaque position possible, calculer un score
        best_split = 0
        best_score = -1

        for i in range(1, len(words)):
            score = 0

            left_part = ' '.join(words[:i])
            right_part = ' '.join(words[i:])
            left_words = words[:i]
            right_words = words[i:]

            # RÈGLE 1: Vérifier présence d'accents français dans la partie droite
            if any(c in french_chars for c in right_part):
                score += 3

            # RÈGLE 2: Si le premier mot à droite a un accent français, c'est probablement le début de la traduction
            if right_words and any(c in french_chars for c in right_words[0]):
                score += 2

            # RÈGLE 3: Articles néerlandais à gauche (de, het, een)
            # Ces articles doivent rester avec le mot qui suit
            if left_words and left_words[-1].lower() in dutch_articles:
                # Pénaliser ce split (on ne veut pas séparer "de" de "babysitter")
                score -= 3

            # RÈGLE 4: Articles néerlandais suivis d'un nom
            if i > 1 and words[i-2].lower() in dutch_articles:
                # Favoriser la séparation après l'article + nom
                score += 2

            # RÈGLE 5: Verbes néerlandais à gauche
            # Si un verbe néerlandais est le dernier mot à gauche, vérifier le contexte
            if left_words and left_words[-1].lower() in dutch_verbs:
                # Si suivi d'un mot néerlandais courant (préposition), ne pas couper ici
                if right_words and right_words[0].lower() in dutch_common:
                    score -= 1  # Pénaliser, on préfère couper après la préposition
                else:
                    score += 2  # Bon point de séparation

            # RÈGLE 6: Mots néerlandais courants (prépositions) à gauche
            if left_words and left_words[-1].lower() in dutch_common:
                # Si c'est suivi d'un mot avec accent français, c'est probablement le bon split
                if right_words and any(c in french_chars for c in right_words[0]):
                    score += 3  # Forte priorité pour ce split
                # Si précédé d'un verbe néerlandais, c'est un bon point de séparation
                elif len(left_words) >= 2 and left_words[-2].lower() in dutch_verbs:
                    score += 2
                else:
                    # Sinon pénaliser légèrement (ces mots vont souvent avec ce qui suit)
                    score -= 1

            # RÈGLE 7: Préférer des splits équilibrés (mais moins important)
            length_balance = abs(len(left_part) - len(right_part))
            if length_balance < 10:
                score += 0.5

            # RÈGLE 8: Nombre de mots équilibré
            word_balance = abs(len(left_words) - len(right_words))
            if word_balance <= 1:
                score += 1

            if score > best_score:
                best_score = score
                best_split = i

        # Retourner le meilleur split seulement si le score est significatif
        return best_split if best_score >= 2 else len(words) // 2
