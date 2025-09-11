import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class TranslationService:
    """Service pour gérer les traductions automatiques."""
    
    # Langues supportées avec codes ISO
    SUPPORTED_LANGUAGES = {
        'fr': 'Français',
        'en': 'Anglais', 
        'es': 'Espagnol',
        'it': 'Italien',
        'de': 'Allemand',
        'pt': 'Portugais',
        'nl': 'Néerlandais',
        'ru': 'Russe',
        'ja': 'Japonais',
        'ko': 'Coréen',
        'zh': 'Chinois',
        'ar': 'Arabe'
    }
    
    def __init__(self):
        """Initialise le service de traduction."""
        # Utilise MyMemory Translation API (gratuit)
        self.base_url = "https://api.mymemory.translated.net/get"
        
    def detect_language(self, text):
        """Détecte automatiquement la langue du texte."""
        try:
            # Utilise l'API LibreTranslate pour la détection (si disponible)
            # Sinon, utilise une heuristique simple basée sur les caractères
            
            # Heuristique simple pour détecter quelques langues courantes
            if any(char in text for char in 'àâäéèêëîïôöùûüÿçñ'):
                return 'fr'
            elif any(char in text for char in 'ñáéíóúü'):
                return 'es'
            elif any(char in text for char in 'àèìòùáéíóú'):
                return 'it'
            elif any(char in text for char in 'äöüß'):
                return 'de'
            elif any(char in text for char in 'ãâàáéêíôõóú'):
                return 'pt'
            else:
                # Par défaut, assume l'anglais
                return 'en'
                
        except Exception as e:
            logger.warning(f"Erreur lors de la détection de langue: {e}")
            return 'en'  # Défaut
    
    def translate_text(self, text, source_lang=None, target_lang='en'):
        """
        Traduit un texte d'une langue source vers une langue cible.
        
        Args:
            text (str): Texte à traduire
            source_lang (str): Code langue source (auto-détection si None)
            target_lang (str): Code langue cible
            
        Returns:
            dict: Résultat de la traduction avec succès et données
        """
        try:
            # Validation des paramètres
            if not text or not text.strip():
                return {
                    'success': False,
                    'error': 'Texte vide'
                }
            
            # Détection automatique de la langue source si non fournie
            if not source_lang:
                source_lang = self.detect_language(text)
            
            # Validation des codes de langue
            if source_lang not in self.SUPPORTED_LANGUAGES:
                source_lang = 'en'
            if target_lang not in self.SUPPORTED_LANGUAGES:
                target_lang = 'en'
            
            # Ne pas traduire si source et cible sont identiques
            if source_lang == target_lang:
                return {
                    'success': True,
                    'translated_text': text,
                    'source_language': source_lang,
                    'target_language': target_lang,
                    'detected_language': source_lang
                }
            
            # Préparer la requête API
            params = {
                'q': text,
                'langpair': f'{source_lang}|{target_lang}',
                'de': 'linguify@example.com'  # Email requis par MyMemory
            }
            
            # Effectuer la requête
            response = requests.get(
                self.base_url, 
                params=params,
                timeout=10,
                headers={'User-Agent': 'Linguify/1.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('responseStatus') == 200:
                    translated_text = data['responseData']['translatedText']
                    
                    return {
                        'success': True,
                        'translated_text': translated_text,
                        'source_language': source_lang,
                        'target_language': target_lang,
                        'detected_language': source_lang,
                        'confidence': data['responseData'].get('match', 0),
                        'provider': 'MyMemory'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Erreur de traduction de l\'API'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Erreur HTTP: {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Délai d\'attente dépassé'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de requête lors de la traduction: {e}")
            return {
                'success': False,
                'error': 'Erreur de connexion'
            }
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la traduction: {e}")
            return {
                'success': False,
                'error': 'Erreur interne'
            }
    
    def get_supported_languages(self):
        """Retourne la liste des langues supportées."""
        return self.SUPPORTED_LANGUAGES
    
    def is_language_supported(self, lang_code):
        """Vérifie si une langue est supportée."""
        return lang_code in self.SUPPORTED_LANGUAGES

# Instance globale du service
translation_service = TranslationService()