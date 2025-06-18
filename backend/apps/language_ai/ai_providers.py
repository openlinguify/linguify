import requests
import logging
import os
import json
from django.conf import settings

logger = logging.getLogger(__name__)

class AIProvider:
    """Classe de base pour les fournisseurs d'IA"""
    
    @classmethod
    def get_provider(cls, provider_name=None):
        """
        Factory method qui retourne le bon fournisseur d'IA.
        Si aucun fournisseur n'est spécifié, cherche dans les settings ou utilise le fournisseur par défaut
        """
        if not provider_name:
            provider_name = getattr(settings, 'AI_PROVIDER', 'openai')
            
        providers = {
            'openai': OpenAIProvider,
            'huggingface': HuggingFaceProvider,
            'ollama': OllamaProvider,
            'simulator': SimulatorProvider
        }
        
        provider_class = providers.get(provider_name.lower(), SimulatorProvider)
        return provider_class()

    def generate_response(self, messages, language, max_tokens=500):
        """Méthode à implémenter par les sous-classes"""
        raise NotImplementedError("Les sous-classes doivent implémenter cette méthode")
    
    def is_available(self):
        """Vérifie si le provider est disponible avec les credentials actuels"""
        return False


class OpenAIProvider(AIProvider):
    """Provider utilisant l'API OpenAI"""
    
    def __init__(self):
        # Requires the openai package: pip install openai
        try:
            import openai
            self.openai = openai
        except ImportError:
            logger.error("OpenAI package not installed. Please run: pip install openai")
            self.openai = None
        
        # Récupérer la clé API
        self.api_key = os.environ.get('OPENAI_API_KEY', None)
        if hasattr(settings, 'OPENAI_API_KEY'):
            self.api_key = settings.OPENAI_API_KEY
        
        # Initialiser le client OpenAI
        if self.api_key:
            self.openai.api_key = self.api_key
            logger.info("OpenAI provider initialized")
        else:
            logger.warning("OpenAI API key not found. Provider will not work.")
    
    def is_available(self):
        return bool(self.api_key) and self.openai is not None
    
    def generate_response(self, messages, language, max_tokens=500):
        if not self.is_available():
            logger.error("OpenAI provider called without API key or missing package")
            return None

        try:
            # Appel à l'API OpenAI
            response = self.openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Le modèle le moins cher
                messages=messages,
                temperature=0.7,
                max_tokens=max_tokens,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            return response.choices[0].message.content.strip()
        except ImportError:
            logger.error("OpenAI package not properly installed")
            return None
        except AttributeError as e:
            logger.error(f"OpenAI API structure error (likely API version mismatch): {str(e)}")
            logger.warning("If you're using OpenAI v1.0+, make sure your code is compatible with the new structure")
            return None
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return None


class HuggingFaceProvider(AIProvider):
    """Provider utilisant Hugging Face Inference API - alternative gratuite"""
    
    def __init__(self):
        # Récupérer le token Hugging Face
        self.hf_token = os.environ.get('HUGGINGFACE_API_TOKEN', None)
        if hasattr(settings, 'HUGGINGFACE_API_TOKEN'):
            self.hf_token = settings.HUGGINGFACE_API_TOKEN
        
        # Modèle par défaut à utiliser (on peut le changer dans les settings)
        self.default_model = getattr(settings, 'HUGGINGFACE_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2')
        
        if self.hf_token:
            logger.info(f"HuggingFace provider initialized with model {self.default_model}")
        else:
            logger.warning("HuggingFace API token not found. Provider will not work properly.")
    
    def is_available(self):
        return bool(self.hf_token)
    
    def generate_response(self, messages, language, max_tokens=500):
        if not self.is_available():
            logger.error("HuggingFace provider called without API token")
            return None
        
        try:
            # Convertir les messages au format attendu par HF
            prompt = self._format_messages_for_hf(messages)
            
            # URL de l'API
            api_url = f"https://api-inference.huggingface.co/models/{self.default_model}"
            
            # En-têtes avec le token d'authentification
            headers = {
                "Authorization": f"Bearer {self.hf_token}",
                "Content-Type": "application/json"
            }
            
            # Préparer le payload
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "return_full_text": False
                }
            }
            
            # Faire la requête
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Extraire la réponse
            result = response.json()
            
            # Le format de la réponse varie selon le modèle
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    return result[0]["generated_text"].strip()
            
            # Fallback si le format n'est pas celui attendu
            return str(result)
            
        except Exception as e:
            logger.error(f"Error calling HuggingFace API: {str(e)}")
            return None
    
    def _format_messages_for_hf(self, messages):
        """Formate les messages pour l'API HuggingFace"""
        # Format pour les modèles type Mistral/Llama-2
        formatted_prompt = ""
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                formatted_prompt += f"<system>\n{content}\n</system>\n\n"
            elif role == "user":
                formatted_prompt += f"<user>\n{content}\n</user>\n\n"
            elif role == "assistant":
                formatted_prompt += f"<assistant>\n{content}\n</assistant>\n\n"
        
        # Ajouter le tag assistant à la fin pour indiquer que c'est au tour de l'assistant de répondre
        formatted_prompt += "<assistant>\n"
        
        return formatted_prompt


class OllamaProvider(AIProvider):
    """Provider utilisant Ollama - pour une solution 100% locale et gratuite"""
    
    def __init__(self):
        # URL de l'API Ollama
        self.api_url = getattr(settings, 'OLLAMA_API_URL', 'http://localhost:11434')
        
        # Modèle par défaut
        self.default_model = getattr(settings, 'OLLAMA_MODEL', 'mistral')
        
        logger.info(f"Ollama provider initialized with model {self.default_model}")
    
    def is_available(self):
        try:
            # Vérifier si l'API Ollama est accessible
            response = requests.get(f"{self.api_url}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, messages, language, max_tokens=500):
        if not self.is_available():
            logger.error("Ollama provider not available or not running")
            return None
        
        try:
            # Convertir les messages au format attendu par Ollama
            prompt = self._format_messages_for_ollama(messages)
            
            # URL pour la génération
            api_url = f"{self.api_url}/api/generate"
            
            # Préparer le payload
            payload = {
                "model": self.default_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.95
                }
            }
            
            # Faire la requête
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            
            # Extraire la réponse
            result = response.json()
            return result.get("response", "").strip()
            
        except Exception as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            return None
    
    def _format_messages_for_ollama(self, messages):
        """Formate les messages pour Ollama"""
        # Format plus simple pour Ollama
        formatted_prompt = ""
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                formatted_prompt += f"SYSTEM: {content}\n"
            elif role == "user":
                formatted_prompt += f"USER: {content}\n"
            elif role == "assistant":
                formatted_prompt += f"ASSISTANT: {content}\n"
        
        # Ajouter le prompt pour la réponse
        formatted_prompt += "ASSISTANT: "
        
        return formatted_prompt


class SimulatorProvider(AIProvider):
    """Provider de simulation (mode hors ligne)"""
    
    def is_available(self):
        # Toujours disponible comme fallback
        return True
    
    def generate_response(self, messages, language, max_tokens=500):
        """Génère une réponse simulée basée sur le message de l'utilisateur"""
        # Trouver le dernier message de l'utilisateur
        user_message = ""
        for message in reversed(messages):
            if message["role"] == "user":
                user_message = message["content"]
                break
        
        # Réponses génériques basées sur la langue
        generic_responses = {
            'en': [
                "That's an interesting point! Could you tell me more about it?",
                "I see what you mean. Have you considered looking at it from another perspective?",
                "That's great! Let's explore this topic further.",
                "I understand. What would you like to discuss next?",
            ],
            'fr': [
                "C'est un point intéressant ! Pourriez-vous m'en dire plus ?",
                "Je comprends ce que vous voulez dire. Avez-vous envisagé de l'examiner sous un autre angle ?",
                "C'est super ! Explorons ce sujet plus en détail.",
                "Je comprends. De quoi aimeriez-vous discuter ensuite ?",
            ],
            'es': [
                "¡Es un punto interesante! ¿Podrías contarme más al respecto?",
                "Entiendo lo que quieres decir. ¿Has considerado verlo desde otra perspectiva?",
                "¡Eso es genial! Exploremos este tema con más detalle.",
                "Entiendo. ¿De qué te gustaría hablar a continuación?",
            ]
        }
        
        # Obtenir les réponses pour la langue spécifiée ou utiliser l'anglais par défaut
        language_responses = generic_responses.get(language, generic_responses['en'])
        
        # Choisir une réponse en fonction de la longueur du message de l'utilisateur
        index = len(user_message) % len(language_responses)
        return language_responses[index]