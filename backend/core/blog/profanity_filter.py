# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

import re
from typing import Dict, List, Tuple
from django.conf import settings
from django.core.cache import cache
from django.db import models


class ProfanityFilter:
    """
    Advanced profanity detection system using secure database storage
    """
    
    def __init__(self):
        """Initialize the profanity filter with database-backed word lists"""
        self.cache_timeout = 3600  # 1 hour cache
        self.profanity_words = self._load_profanity_words()
        self.profanity_patterns = self._create_patterns()
    
    def _load_profanity_words(self) -> set:
        """Load profanity words from database with caching"""
        cache_key = 'profanity_words_set'
        cached_words = cache.get(cache_key)
        
        if cached_words is not None:
            return cached_words
        
        try:
            # Import here to avoid circular imports
            from .models import ProfanityWord
            
            # Load active profanity words from database
            words = set()
            profanity_records = ProfanityWord.objects.filter(is_active=True).values('word')
            words.update([record['word'].lower() for record in profanity_records])
            
            # Cache the results
            cache.set(cache_key, words, self.cache_timeout)
            return words
            
        except Exception as e:
            # Fallback to minimal hardcoded list for emergencies
            return {
                'spam', 'abuse', 'inappropriate', 'offensive'
            }
    
    def _get_severity_mapping(self) -> Dict[str, str]:
        """Get word to severity mapping from database with caching"""
        cache_key = 'profanity_severity_mapping'
        cached_mapping = cache.get(cache_key)
        
        if cached_mapping is not None:
            return cached_mapping
        
        try:
            from .models import ProfanityWord
            
            mapping = {}
            records = ProfanityWord.objects.filter(is_active=True).values('word', 'severity')
            for record in records:
                mapping[record['word'].lower()] = record['severity']
            
            cache.set(cache_key, mapping, self.cache_timeout)
            return mapping
            
        except Exception:
            return {}
    
    def clear_cache(self):
        """Clear profanity word cache - useful after database updates"""
        cache.delete('profanity_words_set')
        cache.delete('profanity_severity_mapping')
        # Reload words
        self.profanity_words = self._load_profanity_words()
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
        
        # Advanced detection for concatenated words and variations (DISABLED to avoid false positives)
        # This was causing "con" to be detected in "content" etc.
        # Commenting out this section for now as word boundary detection above is sufficient
        
        # clean_text = re.sub(r'[^a-zA-Zàáâäæèéêëìíîïòóôöøùúûüÿç]', '', text_lower)
        # for word in self.profanity_words:
        #     clean_word = re.sub(r'[^a-zA-Zàáâäæèéêëìíîïòóôöøùúûüÿç]', '', word)
        #     if len(clean_word) >= 3 and clean_word in clean_text:
        #         found_words.append(word)
        
        # Advanced variant detection using database patterns
        # This section can be enhanced with database-stored variant mappings if needed
        
        # Remove duplicates while preserving order
        found_words = list(dict.fromkeys(found_words))
        
        return len(found_words) > 0, found_words
    
    
    def get_severity_level(self, found_words: List[str]) -> str:
        """
        Determine severity level based on found profanity using database mapping
        
        Args:
            found_words: List of profane words found
            
        Returns:
            Severity level: 'mild', 'moderate', 'severe'
        """
        if not found_words:
            return 'none'
        
        severity_mapping = self._get_severity_mapping()
        
        # Check for highest severity first
        for word in found_words:
            severity = severity_mapping.get(word.lower(), 'mild')
            if severity == 'severe':
                return 'severe'
        
        for word in found_words:
            severity = severity_mapping.get(word.lower(), 'mild')
            if severity == 'moderate':
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