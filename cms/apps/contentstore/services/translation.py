"""
Automatic translation service for course content.
Uses Google Translate or other translation APIs.
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for automatic translation of course content."""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_TRANSLATE_API_KEY', None)
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
    
    def translate_text(self, text, target_language, source_language='fr'):
        """
        Translate text using Google Translate API.
        
        Args:
            text (str): Text to translate
            target_language (str): Target language code (en, es, nl)
            source_language (str): Source language code (default: fr)
            
        Returns:
            str: Translated text or original text if translation fails
        """
        if not text or not text.strip():
            return text
            
        if not self.api_key:
            logger.warning("Google Translate API key not configured, skipping translation")
            return text
            
        try:
            params = {
                'q': text,
                'target': target_language,
                'source': source_language,
                'key': self.api_key,
                'format': 'text'
            }
            
            response = requests.post(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'data' in data and 'translations' in data['data']:
                translated_text = data['data']['translations'][0]['translatedText']
                logger.info(f"Translated text from {source_language} to {target_language}")
                return translated_text
            else:
                logger.error("Unexpected response format from Google Translate")
                return text
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Translation API request failed: {e}")
            return text
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text
    
    def translate_course_content(self, title_fr, description_fr):
        """
        Translate course title and description to all supported languages.
        
        Args:
            title_fr (str): French title
            description_fr (str): French description
            
        Returns:
            dict: Dictionary with translations for all languages
        """
        translations = {
            'title_fr': title_fr,
            'description_fr': description_fr,
            'title_en': '',
            'title_es': '',
            'title_nl': '',
            'description_en': '',
            'description_es': '',
            'description_nl': ''
        }
        
        # Target languages
        languages = ['en', 'es', 'nl']
        
        try:
            # Translate title
            for lang in languages:
                if title_fr:
                    translations[f'title_{lang}'] = self.translate_text(title_fr, lang)
                
                # Translate description
                if description_fr:
                    translations[f'description_{lang}'] = self.translate_text(description_fr, lang)
                    
        except Exception as e:
            logger.error(f"Batch translation failed: {e}")
        
        return translations
    
    def get_fallback_translations(self, title_fr, description_fr):
        """
        Get basic fallback translations when API is not available.
        
        Args:
            title_fr (str): French title
            description_fr (str): French description
            
        Returns:
            dict: Dictionary with basic translations
        """
        return {
            'title_fr': title_fr,
            'description_fr': description_fr,
            'title_en': title_fr,  # Fallback to French
            'title_es': title_fr,
            'title_nl': title_fr,
            'description_en': description_fr,
            'description_es': description_fr,
            'description_nl': description_fr
        }


# Global instance
translation_service = TranslationService()