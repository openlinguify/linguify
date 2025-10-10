"""
Service de traduction utilisant MyMemory (API gratuite, pas de clé requise)
Fallback: LibreTranslate (API gratuite et open-source)
"""
import requests
from typing import Optional, List, Dict
import logging
from functools import lru_cache
import time

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Service pour traduire du texte en utilisant plusieurs APIs gratuites:

    1. MyMemory (primary): API gratuite sans clé API requise
       - Limite: 5000 caractères/jour pour usage anonyme
       - Pas de compte requis

    2. LibreTranslate (fallback): API open-source
       - Instance publique nécessite API key
       - Alternative: self-host avec Docker:
         docker run -ti --rm -p 5000:5000 libretranslate/libretranslate
    """

    # API MyMemory (gratuite, pas de clé requise)
    MYMEMORY_API_URL = "https://api.mymemory.translated.net/get"

    # API LibreTranslate (fallback)
    LIBRETRANSLATE_API_URL = "https://libretranslate.com/translate"

    # Mapping des codes de langue
    LANGUAGE_CODES = {
        'en': 'en',
        'fr': 'fr',
        'es': 'es',
        'de': 'de',
        'it': 'it',
        'pt': 'pt',
        'nl': 'nl',
        'pl': 'pl',
        'ru': 'ru',
        'zh': 'zh',
        'ja': 'ja',
        'ko': 'ko',
        'ar': 'ar',
        'hi': 'hi',
    }

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None, use_mymemory: bool = True):
        """
        Initialise le service de traduction

        Args:
            api_url: URL de l'API LibreTranslate (pour override)
            api_key: Clé API pour LibreTranslate
            use_mymemory: Utiliser MyMemory comme API principale (True par défaut)
        """
        self.libretranslate_url = api_url or self.LIBRETRANSLATE_API_URL
        self.api_key = api_key
        self.use_mymemory = use_mymemory
        self._last_request_time = 0
        self._min_request_interval = 0.5  # 500ms entre requêtes pour respecter les limites

    def _rate_limit(self):
        """Applique un rate limiting simple"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            time.sleep(self._min_request_interval - time_since_last)
        self._last_request_time = time.time()

    @lru_cache(maxsize=1000)
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """
        Traduit un texte d'une langue source vers une langue cible

        Args:
            text: Texte à traduire
            source_lang: Code de la langue source (ex: 'en', 'fr')
            target_lang: Code de la langue cible (ex: 'fr', 'es')

        Returns:
            Texte traduit ou None en cas d'erreur
        """
        # Ne pas traduire si les langues sont identiques
        if source_lang == target_lang:
            return text

        # Vérifier que les langues sont supportées
        if source_lang not in self.LANGUAGE_CODES or target_lang not in self.LANGUAGE_CODES:
            logger.warning(f"Langue non supportée: {source_lang} -> {target_lang}")
            return None

        # Essayer MyMemory en premier si activé
        if self.use_mymemory:
            result = self._translate_mymemory(text, source_lang, target_lang)
            if result:
                return result
            # Si MyMemory échoue, tenter LibreTranslate si une clé API est disponible
            if self.api_key:
                logger.info("MyMemory failed, trying LibreTranslate...")
                return self._translate_libretranslate(text, source_lang, target_lang)
        else:
            # Utiliser LibreTranslate directement
            return self._translate_libretranslate(text, source_lang, target_lang)

        return None

    def _translate_mymemory(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Traduit avec l'API MyMemory (gratuite, pas de clé requise)

        Args:
            text: Texte à traduire
            source_lang: Code langue source
            target_lang: Code langue cible

        Returns:
            Texte traduit ou None
        """
        try:
            self._rate_limit()

            # Limiter la longueur du texte (MyMemory limite à 500 caractères par requête)
            if len(text) > 500:
                logger.warning(f"Text too long for MyMemory ({len(text)} chars), truncating to 500")
                text = text[:500]

            # Préparer les paramètres
            params = {
                'q': text,
                'langpair': f"{self.LANGUAGE_CODES[source_lang]}|{self.LANGUAGE_CODES[target_lang]}"
            }

            # Effectuer la requête GET
            response = requests.get(
                self.MYMEMORY_API_URL,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()

                # Vérifier le statut de la réponse
                if result.get('responseStatus') == 200:
                    translated_text = result.get('responseData', {}).get('translatedText', '')

                    # Vérifier que la traduction n'est pas vide
                    if translated_text and translated_text.strip():
                        logger.info(f"MyMemory: '{text[:50]}...' → '{translated_text[:50]}...' ({source_lang}->{target_lang})")
                        return translated_text
                    else:
                        logger.warning("MyMemory returned empty translation")
                        return None
                else:
                    logger.warning(f"MyMemory API error: {result.get('responseMessage', 'Unknown error')}")
                    return None
            else:
                logger.error(f"MyMemory HTTP error: {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"MyMemory timeout for '{text[:50]}...'")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"MyMemory network error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"MyMemory unexpected error: {str(e)}")
            return None

    def _translate_libretranslate(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Traduit avec l'API LibreTranslate (nécessite clé API pour instance publique)

        Args:
            text: Texte à traduire
            source_lang: Code langue source
            target_lang: Code langue cible

        Returns:
            Texte traduit ou None
        """
        try:
            self._rate_limit()

            # Préparer les données
            data = {
                'q': text,
                'source': self.LANGUAGE_CODES[source_lang],
                'target': self.LANGUAGE_CODES[target_lang],
                'format': 'text'
            }

            # Ajouter la clé API si disponible
            if self.api_key:
                data['api_key'] = self.api_key

            # Effectuer la requête POST
            response = requests.post(
                self.libretranslate_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                translated_text = result.get('translatedText', '')

                logger.info(f"LibreTranslate: '{text[:50]}...' → '{translated_text[:50]}...' ({source_lang}->{target_lang})")
                return translated_text
            else:
                logger.error(f"LibreTranslate error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"LibreTranslate timeout for '{text[:50]}...'")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"LibreTranslate network error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"LibreTranslate unexpected error: {str(e)}")
            return None

    def translate_batch(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str
    ) -> List[Dict[str, str]]:
        """
        Traduit un lot de textes

        Args:
            texts: Liste de textes à traduire
            source_lang: Code de la langue source
            target_lang: Code de la langue cible

        Returns:
            Liste de dictionnaires {'original': '...', 'translated': '...'}
        """
        results = []

        for text in texts:
            translated = self.translate(text, source_lang, target_lang)
            results.append({
                'original': text,
                'translated': translated if translated else text  # Fallback sur l'original
            })

        return results

    def is_available(self) -> bool:
        """
        Vérifie si l'API de traduction est disponible

        Returns:
            True si l'API répond, False sinon
        """
        try:
            # Test simple avec une traduction courte
            result = self.translate("hello", "en", "fr")
            return result is not None
        except:
            return False

    @classmethod
    def get_supported_languages(cls) -> List[str]:
        """
        Retourne la liste des langues supportées

        Returns:
            Liste des codes de langue supportés
        """
        return list(cls.LANGUAGE_CODES.keys())

    def clear_cache(self):
        """Vide le cache de traduction"""
        self.translate.cache_clear()
