# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

import re
from typing import Dict, List, Tuple
from django.conf import settings


class ProfanityFilter:
    """
    Advanced profanity detection system for multiple languages
    """
    
    # English profanity words (comprehensive list)
    ENGLISH_PROFANITY = [
        # Base vulgar words
        'fuck', 'shit', 'damn', 'bitch', 'bastard', 'ass', 'asshole', 
        'crap', 'piss', 'whore', 'slut', 'dick', 'cock', 'pussy',
        'fag', 'faggot', 'nigger', 'retard', 'motherfucker',
        
        # Extended vulgar vocabulary
        'cunt', 'twat', 'tits', 'boobs', 'penis', 'vagina', 'anus',
        'screw', 'hump', 'bang', 'bonk', 'shag', 'scumbag',
        'douchebag', 'dickhead', 'prick', 'turd', 'coon',
        
        # Internet variations and leetspeak
        'f*ck', 'fck', 'fuk', 'fook', 'phuck', 's*it', 'sh*t', 'sht',
        'b*tch', 'btch', 'biatch', 'beotch', 'a$$', 'azz',
        'fukk', 'fucc', 'shyt', 'sheeet', 'shieet', 'dayum'
    ]
    
    # French profanity words (comprehensive list)
    FRENCH_PROFANITY = [
        # Base vulgar words
        'merde', 'putain', 'connard', 'salope', 'pute', 'enculé',
        'bite', 'con', 'conne', 'crétin', 'débile', 'abruti', 'taré', 'foutre', 'chier', 'bordel',
        
        # Insults and derogatory terms
        'bâtard', 'bâtarde', 'salaud', 'salopard', 'saloperie'
        
        # Homophobic slurs
        'pédé', 'tapette', 'lopette', 'tarlouze',
        
        # Racist terms
        'bougnoule', 'bicot', 'raton', 'négro', 'nègre',
        'chintok', 'youpin', 'feuj',
        
        # Vulgar expressions (single words only to avoid regex issues)
        'gueule',
        
        # Internet/text speak variations
        'ptain', 'putin', 'merde', 'connasse', 'salop',
        'encule', 'enculer', 'fdp', 'ptn', 'batard', 'batarde'
    ]
    
    # Spanish profanity words
    SPANISH_PROFANITY = [
        'joder', 'mierda', 'puta', 'cabrón', 'pendejo', 'idiota',
        'estúpido', 'imbécil', 'tonto', 'gilipollas', 'coño',
        'hostia', 'carajo', 'culero', 'mamón'
    ]
    
    # Dutch profanity words
    DUTCH_PROFANITY = [
        'shit', 'kut', 'klootzak', 'hoer', 'lul', 'pik', 'eikel',
        'idioot', 'mongool', 'debiel', 'achterlijk', 'stom',
        'domme', 'sukkel', 'kanker', 'tyfus', 'cholera'
    ]
    
    def __init__(self):
        """Initialize the profanity filter with combined word lists"""
        self.profanity_words = set()
        self.profanity_words.update([word.lower() for word in self.ENGLISH_PROFANITY])
        self.profanity_words.update([word.lower() for word in self.FRENCH_PROFANITY])
        self.profanity_words.update([word.lower() for word in self.SPANISH_PROFANITY])
        self.profanity_words.update([word.lower() for word in self.DUTCH_PROFANITY])
        
        # Create regex patterns for better detection
        self.profanity_patterns = self._create_patterns()
    
    def _create_patterns(self) -> List[re.Pattern]:
        """Create simplified regex patterns for profanity detection"""
        patterns = []
        
        for word in self.profanity_words:
            # Basic word pattern (always safe)
            patterns.append(re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE))
            
            # Simple leetspeak variations (safe patterns only)
            if len(word) >= 3:
                # Replace common characters with safe alternatives
                leetspeak_word = word.replace('a', '[a4@]').replace('e', '[e3]').replace('i', '[i1!]').replace('o', '[o0]')
                if leetspeak_word != word:
                    try:
                        patterns.append(re.compile(r'\b' + leetspeak_word + r'\b', re.IGNORECASE))
                    except re.error:
                        pass
        
        return patterns
    
    
    def contains_profanity(self, text: str) -> Tuple[bool, List[str]]:
        """
        Check if text contains profanity
        
        Args:
            text: Text to check
            
        Returns:
            Tuple of (contains_profanity: bool, found_words: List[str])
        """
        if not text:
            return False, []
        
        text_lower = text.lower()
        found_words = []
        
        # Check against word list
        words = re.findall(r'\b\w+\b', text_lower)
        for word in words:
            if word in self.profanity_words:
                found_words.append(word)
        
        # Check against patterns for variations
        for pattern in self.profanity_patterns:
            matches = pattern.findall(text)
            found_words.extend(matches)
        
        # Advanced detection for concatenated words and variations
        clean_text = re.sub(r'[^a-zA-Zàáâäæèéêëìíîïòóôöøùúûüÿç]', '', text_lower)
        
        # Check if profanity words are contained in cleaned text
        for word in self.profanity_words:
            clean_word = re.sub(r'[^a-zA-Zàáâäæèéêëìíîïòóôöøùúûüÿç]', '', word)
            if len(clean_word) >= 3 and clean_word in clean_text:
                found_words.append(word)
        
        # Check for phonetic and variant spellings
        variant_map = {
            'putin': 'putain', 'poutain': 'putain', 'putein': 'putain', 'putainde': 'putain',
            'conar': 'connard', 'salop': 'salope', 'encule': 'enculé',
            'yupins': 'youpin', 'yupin': 'youpin', 'youping': 'youpin',
            'medeux': 'merde', 'merdeux': 'merde', 'médeux': 'merde'
        }
        
        # Check each word against variants
        for word in words:
            if word in variant_map:
                found_words.append(variant_map[word])
        
        # Check for partial matches in cleaned text for sensitive terms
        sensitive_terms = ['youpin', 'yupin', 'bougnoule', 'bicot', 'raton', 'négro', 'nègre']
        for term in sensitive_terms:
            if term in clean_text or term.replace('ou', 'u') in clean_text:
                found_words.append(term)
        
        # Remove duplicates while preserving order
        found_words = list(dict.fromkeys(found_words))
        
        return len(found_words) > 0, found_words
    
    
    def get_severity_level(self, found_words: List[str]) -> str:
        """
        Determine severity level based on found profanity
        
        Args:
            found_words: List of profane words found
            
        Returns:
            Severity level: 'mild', 'moderate', 'severe'
        """
        if not found_words:
            return 'none'
        
        # Severe: Racist, hate speech, extremely vulgar - MUST BE BLOCKED
        severe_words = {'nigger', 'faggot', 'motherfucker', 'cunt', 'bougnoule', 'nègre', 'bicot', 'raton', 'chintok', 'youpin', 'yupin', 'feuj', 'kanker'}
        
        # Moderate: Strong insults and vulgar terms
        moderate_words = {'fuck', 'shit', 'bitch', 'connard', 'salope', 'pute', 'enculé', 'pédé', 'tapette', 'gilipollas'}
        
        for word in found_words:
            if word.lower() in severe_words:
                return 'severe'
        
        for word in found_words:
            if word.lower() in moderate_words:
                return 'moderate'
        
        return 'mild'
    
    def censor_text(self, text: str, replacement: str = '*') -> str:
        """
        Replace profanity with censoring characters
        
        Args:
            text: Original text
            replacement: Character to use for replacement
            
        Returns:
            Censored text
        """
        censored = text
        
        for pattern in self.profanity_patterns:
            def replace_match(match):
                return replacement * len(match.group())
            censored = pattern.sub(replace_match, censored)
        
        return censored
    
    def get_warning_message(self, severity: str, language: str = 'en') -> str:
        """
        Get appropriate warning message based on severity and language
        
        Args:
            severity: Severity level ('mild', 'moderate', 'severe')
            language: Language code for message
            
        Returns:
            Warning message string
        """
        messages = {
            'en': {
                'mild': 'Please keep your comments respectful. Inappropriate language is not tolerated. Please revise your message.',
                'moderate': 'Your comment contains inappropriate language and cannot be posted. Please revise your message.',
                'severe': 'Your comment contains offensive language and cannot be posted. Please revise your message.'
            },
            'fr': {
                'mild': 'Veuillez garder vos commentaires respectueux. Le langage inapproprié n\'est pas toléré. Veuillez réviser votre message.',
                'moderate': 'Votre commentaire contient un langage inapproprié et ne peut pas être publié. Veuillez réviser votre message.',
                'severe': 'Votre commentaire contient un langage offensant et ne peut pas être publié. Veuillez réviser votre message.'
            },
            'es': {
                'mild': 'Por favor mantenga sus comentarios respetuosos. El lenguaje inapropiado no es tolerado.',
                'moderate': 'Advertencia: Su comentario contiene lenguaje inapropiado. Por favor revise su mensaje.',
                'severe': 'Error: El lenguaje vulgar está estrictamente prohibido. Su comentario no puede ser publicado.'
            },
            'nl': {
                'mild': 'Houd uw opmerkingen respectvol. Ongepaste taal wordt niet getolereerd.',
                'moderate': 'Waarschuwing: Uw opmerking bevat ongepaste taal. Gelieve uw bericht te herzien.',
                'severe': 'Fout: Vulgaire taal is strikt verboden. Uw opmerking kan niet worden geplaatst.'
            }
        }
        
        return messages.get(language, messages['en']).get(severity, messages['en']['mild'])


# Global instance
profanity_filter = ProfanityFilter()


def validate_comment_content(content: str) -> Dict[str, any]:
    """
    Validate comment content for profanity
    
    Args:
        content: Comment content to validate
        
    Returns:
        Dictionary with validation results
    """
    has_profanity, found_words = profanity_filter.contains_profanity(content)
    
    if not has_profanity:
        return {
            'is_valid': True,
            'has_profanity': False,
            'severity': 'none',
            'found_words': [],
            'warning_message': '',
            'censored_content': content
        }
    
    severity = profanity_filter.get_severity_level(found_words)
    warning_message = profanity_filter.get_warning_message(severity, 'en')
    censored_content = profanity_filter.censor_text(content)
    
    # Block ALL profanity - no exceptions
    is_valid = False  # Block any detected profanity
    
    return {
        'is_valid': is_valid,
        'has_profanity': True,
        'severity': severity,
        'found_words': found_words,
        'warning_message': warning_message,
        'censored_content': censored_content
    }