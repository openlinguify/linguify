try:
    import speech_recognition as sr
except ImportError:
    sr = None
import base64
import io
import json
import logging
import re
from typing import Dict, Optional, Any
from apps.authentication.models import User

logger = logging.getLogger(__name__)

class LinguifyAIService:
    """Service IA conversationnel pour Linguify avec Claude"""
    
    def __init__(self):
        self.context_knowledge = self._build_linguify_context()
        
    def _build_linguify_context(self) -> str:
        """Construit le contexte de connaissance sur Linguify"""
        return """
Tu es l'assistant vocal intelligent de Linguify, une plateforme d'apprentissage des langues.

CONTEXTE LINGUIFY:
- Linguify est une plateforme SaaS pour apprendre les langues
- Les utilisateurs ont une langue native (native_language) et une langue cible (target_language)
- Niveaux disponibles: A1, A2, B1, B2, C1, C2
- Applications disponibles: Notes, Révision, Quiz, Learning, Community, Conversation AI
- Langues supportées: Français (FR), Anglais (EN), Espagnol (ES), Néerlandais (NL), Allemand (DE), Italien (IT)

CAPACITÉS DISPONIBLES:
1. Navigation (navigate): dashboard, notes, revision, quiz, learning, community, conversation, profile, settings
2. Informations utilisateur (get_user_info): native_language, target_language, language_level, profile_summary
3. Modification paramètres (update_user_setting): native_language, target_language, language_level  
4. Statistiques (get_user_stats): learning_progress, study_time
5. Infos système (get_system_info): user_count
6. Contrôles (toggle_theme, enable_tts, disable_tts)

PERSONNALITÉ:
- Amical et encourageant pour l'apprentissage
- Adapté à la langue native de l'utilisateur
- Intelligent et proactif dans les suggestions
- Sécurisé (demande confirmation pour modifications importantes)

Tu dois analyser les demandes en langage naturel et les convertir en actions Linguify appropriées.
"""

    def process_natural_language_command(self, user_input: str, user_context: Dict) -> Dict[str, Any]:
        """Traite une commande en langage naturel avec l'IA"""
        try:
            # Analyser la demande avec l'IA
            ai_analysis = self._analyze_with_ai(user_input, user_context)
            
            # Convertir l'analyse en action Linguify
            action_result = self._convert_to_linguify_action(ai_analysis, user_input)
            
            return action_result
            
        except Exception as e:
            logger.error(f"Error in AI processing: {e}")
            return {
                'success': False,
                'action': 'ai_error',
                'response': 'Désolé, je n\'ai pas pu traiter votre demande avec l\'IA.',
                'fallback': True
            }
    
    def _analyze_with_ai(self, user_input: str, user_context: Dict) -> Dict:
        """Analyse la demande avec Claude (intégration réelle)"""
        
        # Utiliser le service Claude réel
        from .services.claude_service import claude_service
        
        try:
            claude_result = claude_service.analyze_voice_command(user_input, user_context)
            
            if claude_result.get('success') and claude_result.get('claude_used'):
                logger.info(f"Claude API utilisée avec succès pour: '{user_input}'")
                return claude_result
            else:
                logger.info(f"Fallback vers patterns pour: '{user_input}'")
                
        except Exception as e:
            logger.error(f"Erreur Claude service: {e}")
        
        # Fallback vers l'analyse par patterns si Claude échoue
        
        input_lower = user_input.lower().strip()
        
        # Patterns d'apprentissage intelligent
        learning_patterns = {
            'progress_inquiry': {
                'patterns': ['comment je progresse', 'où j\'en suis', 'mes progrès', 'ma progression', 'niveau actuel'],
                'intent': 'check_learning_progress',
                'confidence': 0.8
            },
            'recommendation_request': {
                'patterns': ['que me conseilles-tu', 'quoi faire maintenant', 'prochaine étape', 'que puis-je étudier'],
                'intent': 'get_learning_recommendation',
                'confidence': 0.9
            },
            'study_plan': {
                'patterns': ['planifier mes études', 'programme d\'étude', 'organiser mon apprentissage'],
                'intent': 'create_study_plan',
                'confidence': 0.85
            },
            'difficulty_help': {
                'patterns': ['j\'ai des difficultés', 'c\'est trop dur', 'je n\'y arrive pas', 'besoin d\'aide'],
                'intent': 'provide_learning_support',
                'confidence': 0.9
            },
            'motivational_support': {
                'patterns': ['je suis découragé', 'j\'abandonne', 'c\'est difficile', 'motivation'],
                'intent': 'provide_motivation',
                'confidence': 0.85
            }
        }
        
        # Patterns de navigation intelligente
        navigation_patterns = {
            'contextual_navigation': {
                'patterns': ['travaille sur', 'continue mes', 'reprendre', 'où j\'étais'],
                'intent': 'contextual_continue',
                'confidence': 0.8
            },
            'smart_suggestion': {
                'patterns': ['propose-moi', 'suggestion', 'idée d\'activité'],
                'intent': 'suggest_activity',
                'confidence': 0.7
            }
        }
        
        # Analyser l'intention
        best_match = None
        best_confidence = 0
        
        all_patterns = {**learning_patterns, **navigation_patterns}
        
        for pattern_name, pattern_data in all_patterns.items():
            for pattern in pattern_data['patterns']:
                if pattern in input_lower:
                    confidence = pattern_data['confidence']
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = {
                            'intent': pattern_data['intent'],
                            'confidence': confidence,
                            'pattern': pattern_name,
                            'matched_phrase': pattern
                        }
        
        return best_match or {'intent': 'unknown', 'confidence': 0}
    
    def _convert_to_linguify_action(self, ai_analysis: Dict, original_input: str) -> Dict[str, Any]:
        """Convertit l'analyse IA en action Linguify"""
        
        if not ai_analysis or ai_analysis.get('confidence', 0) < 0.5:
            return {
                'success': False,
                'action': 'unknown',
                'response': f"Je ne suis pas sûr de comprendre '{original_input}'. Pouvez-vous reformuler ?",
                'suggestion': "Essayez 'mes progrès' ou 'que me conseilles-tu'"
            }
        
        intent = ai_analysis.get('intent')
        
        # Mapper les intentions aux actions Linguify
        if intent == 'check_learning_progress':
            return {
                'success': True,
                'action': 'get_user_stats',
                'params': {'stats_type': 'learning_progress'},
                'response': 'Voici vos progrès d\'apprentissage',
                'ai_enhanced': True,
                'follow_up': 'Voulez-vous des conseils pour améliorer votre progression ?'
            }
        
        elif intent == 'get_learning_recommendation':
            return {
                'success': True,
                'action': 'ai_recommendation',
                'params': {'recommendation_type': 'next_steps'},
                'response': 'Basé sur votre profil, je vous recommande de commencer par réviser le vocabulaire, puis faire un quiz pour tester vos connaissances.',
                'ai_enhanced': True,
                'suggested_actions': [
                    {'text': 'Aller aux révisions', 'action': 'navigate', 'params': {'url': '/revision/'}},
                    {'text': 'Faire un quiz', 'action': 'navigate', 'params': {'url': '/quizz/'}}
                ]
            }
        
        elif intent == 'create_study_plan':
            return {
                'success': True,
                'action': 'ai_study_plan',
                'params': {'plan_type': 'weekly'},
                'response': 'Je vous propose un plan d\'étude personnalisé : Lundi-Mercredi-Vendredi : 20min de vocabulaire, Mardi-Jeudi : Quiz et conversation, Weekend : Révision générale.',
                'ai_enhanced': True,
                'plan_details': {
                    'duration': '1 semaine',
                    'daily_time': '20-30 minutes',
                    'focus': 'Vocabulaire et pratique'
                }
            }
        
        elif intent == 'provide_learning_support':
            return {
                'success': True,
                'action': 'ai_support',
                'params': {'support_type': 'difficulty_help'},
                'response': 'Je comprends que l\'apprentissage peut être difficile. Essayons une approche différente : commencez par des exercices plus simples en révision, puis progressez graduellement.',
                'ai_enhanced': True,
                'suggested_actions': [
                    {'text': 'Exercices faciles', 'action': 'navigate', 'params': {'url': '/revision/?level=easy'}},
                    {'text': 'Vocabulaire de base', 'action': 'navigate', 'params': {'url': '/learning/?category=vocabulary'}}
                ]
            }
        
        elif intent == 'provide_motivation':
            return {
                'success': True,
                'action': 'ai_motivation',
                'params': {'motivation_type': 'encouragement'},
                'response': 'Ne vous découragez pas ! L\'apprentissage des langues demande du temps. Vous avez déjà fait de beaux progrès. Chaque petite session compte !',
                'ai_enhanced': True,
                'motivational_tip': 'Fixez-vous de petits objectifs quotidiens de 10-15 minutes.'
            }
        
        elif intent == 'suggest_activity':
            return {
                'success': True,
                'action': 'ai_activity_suggestion',
                'params': {'suggestion_type': 'contextual'},
                'response': 'Selon votre niveau et vos dernières activités, je vous propose une session de conversation pour pratiquer ce que vous avez appris récemment.',
                'ai_enhanced': True,
                'suggested_actions': [
                    {'text': 'Conversation AI', 'action': 'navigate', 'params': {'url': '/language_ai/'}},
                    {'text': 'Rejoindre la communauté', 'action': 'navigate', 'params': {'url': '/community/'}}
                ]
            }
        
        # === NOUVELLES ACTIONS FLASHCARD ===
        elif intent == 'create_flashcard':
            # S'assurer que l'action est correcte
            result = dict(ai_analysis)
            result['action'] = 'create_flashcard'
            return result
        
        elif intent == 'extract_and_create_flashcards':
            return {
                'success': True,
                'action': 'extract_vocabulary',
                'params': ai_analysis.get('params', {}),
                'response': ai_analysis.get('response', 'Je vais extraire les mots importants et créer des flashcards.'),
                'ai_enhanced': True,
                'suggested_actions': ai_analysis.get('suggested_actions', [])
            }
        
        # === CONNEXION AVEC LANGUAGE AI ===
        elif intent == 'start_conversation':
            return {
                'success': True,
                'action': 'start_language_conversation',
                'params': ai_analysis.get('params', {}),
                'response': ai_analysis.get('response', 'Je démarre une conversation pour pratiquer votre langue cible.'),
                'ai_enhanced': True,
                'suggested_actions': [
                    {'text': 'Conversation IA', 'action': 'navigate', 'params': {'url': '/language_ai/'}},
                    {'text': 'Choisir un sujet', 'action': 'navigate', 'params': {'url': '/language_ai/?topic=beginner'}}
                ]
            }
        
        else:
            # Si l'intent n'est pas reconnu, mais qu'on a une analyse IA valide, l'utiliser
            if ai_analysis and ai_analysis.get('success'):
                return ai_analysis
            
            return {
                'success': False,
                'action': 'unknown',
                'response': f"Intent '{intent}' reconnu mais pas encore implémenté.",
                'ai_analysis': ai_analysis
            }

class VoiceAssistantService:
    """Service principal pour l'assistant vocal Linguify"""
    
    def __init__(self):
        self.tts_available = False
        self.engine = None
        self._init_tts()
        self.voice_commands = self._load_default_commands()
        self.ai_service = LinguifyAIService()  # Intégration IA
        
    def _init_tts(self):
        """Initialise le moteur TTS"""
        # TTS désactivé - utiliser Web Speech API côté client
        self.tts_available = False
        self.engine = None
        logger.info("TTS désactivé - utilisation de Web Speech API recommandée")
    
    def get_language_mapping(self) -> Dict[str, str]:
        """Retourne le mapping des codes de langue pour la reconnaissance vocale"""
        return {
            'en': 'en-US',
            'fr': 'fr-FR', 
            'es': 'es-ES',
            'de': 'de-DE',
            'it': 'it-IT',
            'pt': 'pt-PT',
            'nl': 'nl-NL',
            'ru': 'ru-RU',
            'ja': 'ja-JP',
            'zh': 'zh-CN',
            'ar': 'ar-SA',
            # Aliases pour compatibility
            'dutch': 'nl-NL',
            'spanish': 'es-ES',
            'english': 'en-US',
            'french': 'fr-FR',
            'german': 'de-DE'
        }
    
    def get_tts_engine(self, language: str = 'en'):
        """Retourne le moteur TTS configuré"""
        if not self.tts_available:
            return None
        return self.engine
    
    def get_speech_recognizer(self):
        """Retourne un recognizer configuré"""
        return sr.Recognizer()
    
    def _load_default_commands(self) -> Dict[str, Dict]:
        """Charge les commandes vocales par défaut pour Linguify"""
        return self._get_commands_for_language('fr')  # Langue par défaut
    
    def _get_commands_for_language(self, language: str = 'fr') -> Dict[str, Dict]:
        """Retourne les commandes vocales dans la langue spécifiée"""
        
        # Normaliser la langue d'entrée
        if not language:
            language = 'fr'
        
        clean_language = str(language).lower().strip()
        logger.info(f"Getting commands for language: '{clean_language}'")
        
        if clean_language in ['en', 'english', 'anglais']:
            logger.info("Returning English commands")
            return self._get_english_commands()
        elif clean_language in ['es', 'spanish', 'español', 'espagnol']:
            logger.info("Returning Spanish commands")
            return self._get_spanish_commands()
        elif clean_language in ['nl', 'dutch', 'nederlands', 'néerlandais']:
            logger.info("Returning Dutch commands")
            return self._get_dutch_commands()
        elif clean_language in ['fr', 'french', 'français', 'francais']:
            logger.info("Returning French commands")
            return self._get_french_commands()
        
        # French commands (default)
        logger.info(f"No match found for '{clean_language}', returning French commands as default")
        return self._get_french_commands()
    
    def _get_english_commands(self) -> Dict[str, Dict]:
        """Commandes vocales en anglais"""
        return {
            # Main Navigation - English
            'go to dashboard': {
                'action': 'navigate',
                'params': {'url': '/dashboard/', 'page': 'dashboard'},
                'response': 'Navigating to dashboard'
            },
            'dashboard': {
                'action': 'navigate',
                'params': {'url': '/dashboard/', 'page': 'dashboard'},
                'response': 'Going to dashboard'
            },
            'go to app store': {
                'action': 'navigate',
                'params': {'url': '/app-store/', 'page': 'app_store'},
                'response': 'Opening app store'
            },
            'app store': {
                'action': 'navigate',
                'params': {'url': '/app-store/', 'page': 'app_store'},
                'response': 'Opening app store'
            },
            
            # Linguify Apps - English
            'go to notes': {
                'action': 'navigate',
                'params': {'url': '/notebook/', 'page': 'notebook'},
                'response': 'Opening Notes app'
            },
            'notes': {
                'action': 'navigate',
                'params': {'url': '/notebook/', 'page': 'notebook'},
                'response': 'Opening Notes app'
            },
            'go to revision': {
                'action': 'navigate',
                'params': {'url': '/revision/', 'page': 'revision'},
                'response': 'Opening Revision app'
            },
            'revision': {
                'action': 'navigate',
                'params': {'url': '/revision/', 'page': 'revision'},
                'response': 'Opening Revision app'
            },
            'go to learning': {
                'action': 'navigate',
                'params': {'url': '/learning/', 'page': 'learning'},
                'response': 'Opening Learning app'
            },
            'learning': {
                'action': 'navigate',
                'params': {'url': '/learning/', 'page': 'learning'},
                'response': 'Opening Learning app'
            },
            'go to quiz': {
                'action': 'navigate',
                'params': {'url': '/quizz/', 'page': 'quizz'},
                'response': 'Opening Quiz app'
            },
            'quiz': {
                'action': 'navigate',
                'params': {'url': '/quizz/', 'page': 'quizz'},
                'response': 'Opening Quiz app'
            },
            'go to community': {
                'action': 'navigate',
                'params': {'url': '/community/', 'page': 'community'},
                'response': 'Opening Community'
            },
            'community': {
                'action': 'navigate',
                'params': {'url': '/community/', 'page': 'community'},
                'response': 'Opening Community'
            },
            'go to chat': {
                'action': 'navigate',
                'params': {'url': '/language_ai/', 'page': 'language_ai'},
                'response': 'Opening Conversation AI'
            },
            'conversation': {
                'action': 'navigate',
                'params': {'url': '/language_ai/', 'page': 'language_ai'},
                'response': 'Opening Conversation AI'
            },
            
            # Settings and Controls - English
            'go to profile': {
                'action': 'navigate',
                'params': {'url': '/profile/', 'page': 'profile'},
                'response': 'Going to your profile'
            },
            'go to settings': {
                'action': 'navigate',
                'params': {'url': '/settings/', 'page': 'settings'},
                'response': 'Opening settings'
            },
            'enable dark mode': {
                'action': 'toggle_theme',
                'params': {'theme': 'dark'},
                'response': 'Dark mode enabled'
            },
            'enable light mode': {
                'action': 'toggle_theme',
                'params': {'theme': 'light'},
                'response': 'Light mode enabled'
            },
            'enable speech': {
                'action': 'enable_tts',
                'params': {},
                'response': 'Text to speech enabled'
            },
            'disable speech': {
                'action': 'disable_tts',
                'params': {},
                'response': 'Text to speech disabled'
            },
            'help': {
                'action': 'show_help',
                'params': {},
                'response': 'Available commands: go to dashboard, notes, revision, quiz, learning, community, conversation, help'
            },
            'what can I say': {
                'action': 'list_commands',
                'params': {},
                'response': 'You can say: dashboard, notes, revision, quiz, learning, community, conversation, help'
            }
        }
        
        # Should not reach here, but fallback to French
        return self._get_french_commands()
    
    def _get_french_commands(self) -> Dict[str, Dict]:
        """Commandes vocales en français avec support multilingue mixte"""
        return {
            # Navigation principale
            'aller au tableau de bord': {
                'action': 'navigate',
                'params': {'url': '/dashboard/', 'page': 'dashboard'},
                'response': 'Navigation vers le tableau de bord'
            },
            'tableau de bord': {
                'action': 'navigate',
                'params': {'url': '/dashboard/', 'page': 'dashboard'},
                'response': 'Retour au tableau de bord'
            },
            # Commandes mixtes français-anglais
            'aller au dashboard': {
                'action': 'navigate',
                'params': {'url': '/dashboard/', 'page': 'dashboard'},
                'response': 'Navigation vers le tableau de bord'
            },
            'dashboard': {
                'action': 'navigate',
                'params': {'url': '/dashboard/', 'page': 'dashboard'},
                'response': 'Retour au tableau de bord'
            },
            'aller au magasin': {
                'action': 'navigate',
                'params': {'url': '/app-store/', 'page': 'app_store'},
                'response': 'Navigation vers le magasin d\'applications'
            },
            'app store': {
                'action': 'navigate',
                'params': {'url': '/app-store/', 'page': 'app_store'},
                'response': 'Ouverture du magasin d\'applications'
            },
            'magasin': {
                'action': 'navigate',
                'params': {'url': '/app-store/', 'page': 'app_store'},
                'response': 'Ouverture du magasin d\'applications'
            },
            
            # Applications Linguify
            'aller aux notes': {
                'action': 'navigate',
                'params': {'url': '/notebook/', 'page': 'notebook'},
                'response': 'Navigation vers l\'application Notes'
            },
            # Commandes mixtes pour applications
            'notes': {
                'action': 'navigate',
                'params': {'url': '/notebook/', 'page': 'notebook'},
                'response': 'Ouverture de l\'application Notes'
            },
            'aller à révision': {
                'action': 'navigate',
                'params': {'url': '/revision/', 'page': 'revision'},
                'response': 'Navigation vers l\'application Révision'
            },
            'aller aux cours': {
                'action': 'navigate',
                'params': {'url': '/learning/', 'page': 'learning'},
                'response': 'Navigation vers l\'application Learning'
            },
            'aller aux quiz': {
                'action': 'navigate',
                'params': {'url': '/quizz/', 'page': 'quizz'},
                'response': 'Navigation vers l\'application Quiz Interactif'
            },
            'aller à la communauté': {
                'action': 'navigate',
                'params': {'url': '/community/', 'page': 'community'},
                'response': 'Navigation vers la Communauté'
            },
            'aller au chat': {
                'action': 'navigate',
                'params': {'url': '/language_ai/', 'page': 'language_ai'},
                'response': 'Navigation vers Conversation AI'
            },
            
            # Navigation simplifiée
            'notes': {
                'action': 'navigate',
                'params': {'url': '/notebook/', 'page': 'notebook'},
                'response': 'Ouverture de l\'application Notes'
            },
            'révision': {
                'action': 'navigate',
                'params': {'url': '/revision/', 'page': 'revision'},
                'response': 'Ouverture de l\'application Révision'
            },
            'cours': {
                'action': 'navigate',
                'params': {'url': '/learning/', 'page': 'learning'},
                'response': 'Ouverture de l\'application Learning'
            },
            'quiz': {
                'action': 'navigate',
                'params': {'url': '/quizz/', 'page': 'quizz'},
                'response': 'Ouverture de l\'application Quiz'
            },
            'communauté': {
                'action': 'navigate',
                'params': {'url': '/community/', 'page': 'community'},
                'response': 'Ouverture de la Communauté'
            },
            'conversation': {
                'action': 'navigate',
                'params': {'url': '/language_ai/', 'page': 'language_ai'},
                'response': 'Ouverture de Conversation AI'
            },
            
            # Profil et paramètres
            'aller au profil': {
                'action': 'navigate',
                'params': {'url': '/profile/', 'page': 'profile'},
                'response': 'Navigation vers votre profil'
            },
            'aller aux paramètres': {
                'action': 'navigate',
                'params': {'url': '/settings/', 'page': 'settings'},
                'response': 'Navigation vers les paramètres'
            },
            # Commandes mixtes pour paramètres
            'aller aux settings': {
                'action': 'navigate',
                'params': {'url': '/settings/', 'page': 'settings'},
                'response': 'Navigation vers les paramètres'
            },
            'settings': {
                'action': 'navigate',
                'params': {'url': '/settings/', 'page': 'settings'},
                'response': 'Ouverture des paramètres'
            },
            'aller dans settings': {
                'action': 'navigate',
                'params': {'url': '/settings/', 'page': 'settings'},
                'response': 'Navigation vers les paramètres'
            },
            'paramètres': {
                'action': 'navigate',
                'params': {'url': '/settings/', 'page': 'settings'},
                'response': 'Ouverture des paramètres'
            },
            # Commandes mixtes courantes
            'profil': {
                'action': 'navigate',
                'params': {'url': '/profile/', 'page': 'profile'},
                'response': 'Navigation vers votre profil'
            },
            'profile': {
                'action': 'navigate',
                'params': {'url': '/profile/', 'page': 'profile'},
                'response': 'Navigation vers votre profil'
            },
            'aller au profil': {
                'action': 'navigate',
                'params': {'url': '/profile/', 'page': 'profile'},
                'response': 'Navigation vers votre profil'
            },
            'go to dashboard': {
                'action': 'navigate',
                'params': {'url': '/dashboard/', 'page': 'dashboard'},
                'response': 'Navigation vers le tableau de bord'
            },
            'go to settings': {
                'action': 'navigate',
                'params': {'url': '/settings/', 'page': 'settings'},
                'response': 'Navigation vers les paramètres'
            },
            
            # Apprentissage
            'commencer une leçon': {
                'action': 'start_lesson',
                'params': {},
                'response': 'Démarrage d\'une nouvelle leçon'
            },
            'faire un quiz': {
                'action': 'start_quiz',
                'params': {},
                'response': 'Démarrage d\'un quiz'
            },
            'réviser le vocabulaire': {
                'action': 'review_vocabulary',
                'params': {},
                'response': 'Démarrage de la révision de vocabulaire'
            },
            'pratiquer la prononciation': {
                'action': 'practice_pronunciation',
                'params': {},
                'response': 'Démarrage de la pratique de prononciation'
            },
            
            # Contrôles vocaux
            'activer la lecture': {
                'action': 'enable_tts',
                'params': {},
                'response': 'Lecture vocale activée'
            },
            'désactiver la lecture': {
                'action': 'disable_tts',
                'params': {},
                'response': 'Lecture vocale désactivée'
            },
            'parler plus lentement': {
                'action': 'change_speed',
                'params': {'speed': 'slow'},
                'response': 'Vitesse de lecture ralentie'
            },
            'parler plus vite': {
                'action': 'change_speed', 
                'params': {'speed': 'fast'},
                'response': 'Vitesse de lecture accélérée'
            },
            
            # Contrôles de thème
            'mode sombre': {
                'action': 'toggle_theme',
                'params': {'theme': 'dark'},
                'response': 'Mode sombre activé'
            },
            'mode clair': {
                'action': 'toggle_theme',
                'params': {'theme': 'light'},
                'response': 'Mode clair activé'
            },
            'activer le mode sombre': {
                'action': 'toggle_theme',
                'params': {'theme': 'dark'},
                'response': 'Mode sombre activé'
            },
            'activer le mode clair': {
                'action': 'toggle_theme',
                'params': {'theme': 'light'},
                'response': 'Mode clair activé'
            },
            
            # Commandes d'information système
            'quelle est ma langue native': {
                'action': 'get_user_info',
                'params': {'info_type': 'native_language'},
                'response': 'Votre langue native est {native_language}'
            },
            'quel est mon niveau de langue': {
                'action': 'get_user_info',
                'params': {'info_type': 'language_level'},
                'response': 'Votre niveau de langue est {language_level}'
            },
            'quelle langue j\'apprends': {
                'action': 'get_user_info',
                'params': {'info_type': 'target_language'},
                'response': 'Vous apprenez le {target_language}'
            },
            'mes informations': {
                'action': 'get_user_info',
                'params': {'info_type': 'profile_summary'},
                'response': 'Profil : {username}, langue native : {native_language}, vous apprenez le {target_language}, niveau {language_level}'
            },
            
            # Commandes de modification des paramètres
            'changer ma langue native en anglais': {
                'action': 'update_user_setting',
                'params': {'setting': 'native_language', 'value': 'EN'},
                'response': 'Langue native changée en anglais',
                'confirmation_required': True
            },
            'changer ma langue native en français': {
                'action': 'update_user_setting',
                'params': {'setting': 'native_language', 'value': 'FR'},
                'response': 'Langue native changée en français',
                'confirmation_required': True
            },
            'changer ma langue native en espagnol': {
                'action': 'update_user_setting',
                'params': {'setting': 'native_language', 'value': 'ES'},
                'response': 'Langue native changée en espagnol',
                'confirmation_required': True
            },
            'changer ma langue native en néerlandais': {
                'action': 'update_user_setting',
                'params': {'setting': 'native_language', 'value': 'NL'},
                'response': 'Langue native changée en néerlandais',
                'confirmation_required': True
            },
            
            # Commandes de changement de langue cible
            'je veux apprendre l\'anglais': {
                'action': 'update_user_setting',
                'params': {'setting': 'target_language', 'value': 'EN'},
                'response': 'Langue cible changée vers l\'anglais',
                'confirmation_required': True
            },
            'je veux apprendre le français': {
                'action': 'update_user_setting',
                'params': {'setting': 'target_language', 'value': 'FR'},
                'response': 'Langue cible changée vers le français',
                'confirmation_required': True
            },
            'je veux apprendre l\'espagnol': {
                'action': 'update_user_setting',
                'params': {'setting': 'target_language', 'value': 'ES'},
                'response': 'Langue cible changée vers l\'espagnol',
                'confirmation_required': True
            },
            
            # Commandes de niveau
            'changer mon niveau en débutant': {
                'action': 'update_user_setting',
                'params': {'setting': 'language_level', 'value': 'A1'},
                'response': 'Niveau changé en débutant (A1)',
                'confirmation_required': True
            },
            'changer mon niveau en intermédiaire': {
                'action': 'update_user_setting',
                'params': {'setting': 'language_level', 'value': 'B1'},
                'response': 'Niveau changé en intermédiaire (B1)',
                'confirmation_required': True
            },
            'changer mon niveau en avancé': {
                'action': 'update_user_setting',
                'params': {'setting': 'language_level', 'value': 'C1'},
                'response': 'Niveau changé en avancé (C1)',
                'confirmation_required': True
            },
            
            # Commandes d'information système Linguify
            'combien d\'utilisateurs sur linguify': {
                'action': 'get_system_info',
                'params': {'info_type': 'user_count'},
                'response': 'Linguify compte actuellement {user_count} utilisateurs'
            },
            'quelles sont mes statistiques': {
                'action': 'get_user_stats',
                'params': {'stats_type': 'learning_progress'},
                'response': 'Vous avez complété {lessons_completed} leçons, avec un niveau de progression de {progress_percentage}%'
            },
            'combien de temps j\'ai étudié': {
                'action': 'get_user_stats',
                'params': {'stats_type': 'study_time'},
                'response': 'Vous avez étudié {total_study_minutes} minutes au total cette semaine'
            },
            
            # Aide et informations
            'aide': {
                'action': 'show_help',
                'params': {},
                'response': 'Voici les commandes disponibles: aller au tableau de bord, commencer une leçon, faire un quiz, réviser le vocabulaire...'
            },
            'que puis-je dire': {
                'action': 'list_commands',
                'params': {},
                'response': 'Vous pouvez dire: aller au tableau de bord, commencer une leçon, faire un quiz, réviser le vocabulaire, pratiquer la prononciation'
            }
        }
    
    def _get_spanish_commands(self) -> Dict[str, Dict]:
        """Commandes vocales en espagnol"""
        return {
            # Navegación principal - Español
            'ir al panel': {
                'action': 'navigate',
                'params': {'url': '/dashboard/', 'page': 'dashboard'},
                'response': 'Navegando al panel principal'
            },
            'panel': {
                'action': 'navigate',
                'params': {'url': '/dashboard/', 'page': 'dashboard'},
                'response': 'Volviendo al panel'
            },
            'ir a la tienda': {
                'action': 'navigate',
                'params': {'url': '/app-store/', 'page': 'app_store'},
                'response': 'Abriendo la tienda de aplicaciones'
            },
            'tienda': {
                'action': 'navigate',
                'params': {'url': '/app-store/', 'page': 'app_store'},
                'response': 'Abriendo la tienda'
            },
            
            # Aplicaciones Linguify - Español
            'ir a notas': {
                'action': 'navigate',
                'params': {'url': '/notebook/', 'page': 'notebook'},
                'response': 'Abriendo la aplicación de Notas'
            },
            'notas': {
                'action': 'navigate',
                'params': {'url': '/notebook/', 'page': 'notebook'},
                'response': 'Abriendo Notas'
            },
            'ir a revisión': {
                'action': 'navigate',
                'params': {'url': '/revision/', 'page': 'revision'},
                'response': 'Abriendo la aplicación de Revisión'
            },
            'revisión': {
                'action': 'navigate',
                'params': {'url': '/revision/', 'page': 'revision'},
                'response': 'Abriendo Revisión'
            },
            'ir a aprendizaje': {
                'action': 'navigate',
                'params': {'url': '/learning/', 'page': 'learning'},
                'response': 'Abriendo la aplicación de Aprendizaje'
            },
            'aprendizaje': {
                'action': 'navigate',
                'params': {'url': '/learning/', 'page': 'learning'},
                'response': 'Abriendo Aprendizaje'
            },
            'ir a cuestionarios': {
                'action': 'navigate',
                'params': {'url': '/quizz/', 'page': 'quizz'},
                'response': 'Abriendo Cuestionarios Interactivos'
            },
            'cuestionarios': {
                'action': 'navigate',
                'params': {'url': '/quizz/', 'page': 'quizz'},
                'response': 'Abriendo Cuestionarios'
            },
            'ir a comunidad': {
                'action': 'navigate',
                'params': {'url': '/community/', 'page': 'community'},
                'response': 'Abriendo la Comunidad'
            },
            'comunidad': {
                'action': 'navigate',
                'params': {'url': '/community/', 'page': 'community'},
                'response': 'Abriendo Comunidad'
            },
            'ir al chat': {
                'action': 'navigate',
                'params': {'url': '/language_ai/', 'page': 'language_ai'},
                'response': 'Abriendo Conversación AI'
            },
            'conversación': {
                'action': 'navigate',
                'params': {'url': '/language_ai/', 'page': 'language_ai'},
                'response': 'Abriendo Conversación AI'
            },
            
            # Perfil y configuración - Español
            'ir al perfil': {
                'action': 'navigate',
                'params': {'url': '/profile/', 'page': 'profile'},
                'response': 'Navegando a tu perfil'
            },
            'ir a configuración': {
                'action': 'navigate',
                'params': {'url': '/settings/', 'page': 'settings'},
                'response': 'Abriendo configuración'
            },
            
            # Controles de tema - Español
            'modo oscuro': {
                'action': 'toggle_theme',
                'params': {'theme': 'dark'},
                'response': 'Modo oscuro activado'
            },
            'modo claro': {
                'action': 'toggle_theme',
                'params': {'theme': 'light'},
                'response': 'Modo claro activado'
            },
            'activar modo oscuro': {
                'action': 'toggle_theme',
                'params': {'theme': 'dark'},
                'response': 'Modo oscuro activado'
            },
            'activar modo claro': {
                'action': 'toggle_theme',
                'params': {'theme': 'light'},
                'response': 'Modo claro activado'
            },
            
            # Controles vocales - Español
            'activar lectura': {
                'action': 'enable_tts',
                'params': {},
                'response': 'Síntesis de voz activada'
            },
            'desactivar lectura': {
                'action': 'disable_tts',
                'params': {},
                'response': 'Síntesis de voz desactivada'
            },
            'hablar más lento': {
                'action': 'change_speed',
                'params': {'speed': 'slow'},
                'response': 'Velocidad de lectura reducida'
            },
            'hablar más rápido': {
                'action': 'change_speed',
                'params': {'speed': 'fast'},
                'response': 'Velocidad de lectura acelerada'
            },
            
            # Ayuda - Español
            'ayuda': {
                'action': 'show_help',
                'params': {},
                'response': 'Comandos disponibles: ir al panel, notas, revisión, cuestionarios, aprendizaje, comunidad, conversación, ayuda'
            },
            'qué puedo decir': {
                'action': 'list_commands',
                'params': {},
                'response': 'Puedes decir: panel, notas, revisión, cuestionarios, aprendizaje, comunidad, conversación, ayuda'
            }
        }
    
    def _get_dutch_commands(self) -> Dict[str, Dict]:
        """Commandes vocales en néerlandais"""
        return {
            # Hoofdnavigatie - Nederlands
            'ga naar dashboard': {
                'action': 'navigate',
                'params': {'url': '/dashboard/', 'page': 'dashboard'},
                'response': 'Navigeren naar het dashboard'
            },
            'dashboard': {
                'action': 'navigate',
                'params': {'url': '/dashboard/', 'page': 'dashboard'},
                'response': 'Terug naar dashboard'
            },
            'ga naar de winkel': {
                'action': 'navigate',
                'params': {'url': '/app-store/', 'page': 'app_store'},
                'response': 'App-winkel openen'
            },
            'winkel': {
                'action': 'navigate',
                'params': {'url': '/app-store/', 'page': 'app_store'},
                'response': 'Winkel openen'
            },
            
            # Linguify Apps - Nederlands
            'ga naar notities': {
                'action': 'navigate',
                'params': {'url': '/notebook/', 'page': 'notebook'},
                'response': 'Notities-app openen'
            },
            'notities': {
                'action': 'navigate',
                'params': {'url': '/notebook/', 'page': 'notebook'},
                'response': 'Notities openen'
            },
            'ga naar revisie': {
                'action': 'navigate',
                'params': {'url': '/revision/', 'page': 'revision'},
                'response': 'Revisie-app openen'
            },
            'revisie': {
                'action': 'navigate',
                'params': {'url': '/revision/', 'page': 'revision'},
                'response': 'Revisie openen'
            },
            'ga naar leren': {
                'action': 'navigate',
                'params': {'url': '/learning/', 'page': 'learning'},
                'response': 'Leer-app openen'
            },
            'leren': {
                'action': 'navigate',
                'params': {'url': '/learning/', 'page': 'learning'},
                'response': 'Leren openen'
            },
            'ga naar quiz': {
                'action': 'navigate',
                'params': {'url': '/quizz/', 'page': 'quizz'},
                'response': 'Interactieve Quiz openen'
            },
            'quiz': {
                'action': 'navigate',
                'params': {'url': '/quizz/', 'page': 'quizz'},
                'response': 'Quiz openen'
            },
            'ga naar gemeenschap': {
                'action': 'navigate',
                'params': {'url': '/community/', 'page': 'community'},
                'response': 'Gemeenschap openen'
            },
            'gemeenschap': {
                'action': 'navigate',
                'params': {'url': '/community/', 'page': 'community'},
                'response': 'Gemeenschap openen'
            },
            'ga naar chat': {
                'action': 'navigate',
                'params': {'url': '/language_ai/', 'page': 'language_ai'},
                'response': 'Conversatie AI openen'
            },
            'conversatie': {
                'action': 'navigate',
                'params': {'url': '/language_ai/', 'page': 'language_ai'},
                'response': 'Conversatie AI openen'
            },
            
            # Profiel en instellingen - Nederlands
            'ga naar profiel': {
                'action': 'navigate',
                'params': {'url': '/profile/', 'page': 'profile'},
                'response': 'Navigeren naar je profiel'
            },
            'ga naar instellingen': {
                'action': 'navigate',
                'params': {'url': '/settings/', 'page': 'settings'},
                'response': 'Instellingen openen'
            },
            
            # Thema-besturing - Nederlands
            'donkere modus': {
                'action': 'toggle_theme',
                'params': {'theme': 'dark'},
                'response': 'Donkere modus geactiveerd'
            },
            'lichte modus': {
                'action': 'toggle_theme',
                'params': {'theme': 'light'},
                'response': 'Lichte modus geactiveerd'
            },
            'activeer donkere modus': {
                'action': 'toggle_theme',
                'params': {'theme': 'dark'},
                'response': 'Donkere modus geactiveerd'
            },
            'activeer lichte modus': {
                'action': 'toggle_theme',
                'params': {'theme': 'light'},
                'response': 'Lichte modus geactiveerd'
            },
            
            # Spraakbesturing - Nederlands
            'activeer voorlezen': {
                'action': 'enable_tts',
                'params': {},
                'response': 'Tekst-naar-spraak geactiveerd'
            },
            'deactiveer voorlezen': {
                'action': 'disable_tts',
                'params': {},
                'response': 'Tekst-naar-spraak gedeactiveerd'
            },
            'spreek langzamer': {
                'action': 'change_speed',
                'params': {'speed': 'slow'},
                'response': 'Spreeksnelheid verlaagd'
            },
            'spreek sneller': {
                'action': 'change_speed',
                'params': {'speed': 'fast'},
                'response': 'Spreeksnelheid verhoogd'
            },
            
            # Hulp - Nederlands
            'help': {
                'action': 'show_help',
                'params': {},
                'response': 'Beschikbare commando\'s: ga naar dashboard, notities, revisie, quiz, leren, gemeenschap, conversatie, help'
            },
            'wat kan ik zeggen': {
                'action': 'list_commands',
                'params': {},
                'response': 'Je kunt zeggen: dashboard, notities, revisie, quiz, leren, gemeenschap, conversatie, help'
            }
        }
    
    def update_commands_for_user(self, user):
        """Met à jour les commandes vocales selon les préférences de l'utilisateur"""
        if user and hasattr(user, 'native_language'):
            user_language = user.native_language.lower()
            # Charger commandes par défaut + commandes personnalisées
            self.voice_commands = self._get_commands_for_language(user_language)
            # Ajouter les commandes personnalisées de l'utilisateur
            custom_commands = self.get_user_custom_commands(user)
            self.voice_commands.update(custom_commands)
        else:
            self.voice_commands = self._get_commands_for_language('fr')
    
    def process_voice_command(self, command_text: str, user=None) -> Dict[str, Any]:
        """Traite une commande vocale et retourne l'action à effectuer"""
        try:
            if not command_text or not command_text.strip():
                return {
                    'success': False,
                    'action': 'error',
                    'params': {},
                    'response': 'Aucune commande fournie',
                    'command': '',
                    'confidence': 0.0
                }
            
            # Mettre à jour les commandes selon l'utilisateur
            if user:
                self.update_commands_for_user(user)
                
            command_text_lower = command_text.lower().strip()
            
            # Recherche exacte
            if command_text_lower in self.voice_commands:
                command = self.voice_commands[command_text_lower]
                return {
                    'success': True,
                    'action': command['action'],
                    'params': command['params'],
                    'response': command['response'],
                    'command': command_text_lower,
                    'confidence': 1.0
                }
            
            # Recherche approximative (mots-clés)
            best_match = None
            best_score = 0
            
            for command_phrase, command_data in self.voice_commands.items():
                if self._fuzzy_match(command_text_lower, command_phrase):
                    # Calculer un score de correspondance
                    input_words = set(command_text_lower.split())
                    command_words = set(command_phrase.split())
                    score = len(input_words.intersection(command_words)) / len(command_words)
                    
                    if score > best_score:
                        best_score = score
                        best_match = (command_phrase, command_data)
            
            if best_match:
                command_phrase, command_data = best_match
                return {
                    'success': True,
                    'action': command_data['action'],
                    'params': command_data['params'], 
                    'response': command_data['response'],
                    'command': command_phrase,
                    'confidence': best_score,
                    'matched_fuzzy': True
                }
            
            # Recherche sémantique avancée pour les commandes non reconnues
            semantic_result = self._semantic_match(command_text)
            if semantic_result:
                logger.info(f"Semantic match found for '{command_text}': {semantic_result['pattern']}")
                return semantic_result
            
            # === NOUVEAU : Traitement IA pour commandes complexes ===
            # Si aucune commande directe n'est trouvée, essayer l'IA AVANT le fallback
            try:
                user_context = self._build_user_context(user) if user else {}
                
                # Vérifier si c'est une commande qui pourrait être traitée par l'IA
                ai_keywords = ['créer', 'flashcard', 'carte', 'vocabulaire', 'ajouter', 'apprendre', 'réviser', 'mémoriser']
                if any(keyword in command_text_lower for keyword in ai_keywords):
                    logger.info(f"Tentative de traitement IA pour: '{command_text}'")
                    
                    ai_result = self.ai_service.process_natural_language_command(command_text, user_context)
                    
                    if ai_result.get('success', False):
                        logger.info(f"AI processing successful for '{command_text}': {ai_result.get('action')}")
                        return ai_result
                    else:
                        logger.info(f"AI processing failed for '{command_text}': {ai_result.get('response', 'Unknown error')}")
                        
            except Exception as e:
                logger.error(f"Error in AI processing for '{command_text}': {e}")
                # Continuer vers le fallback normal en cas d'erreur IA
            
            # Commande non reconnue - adapter le message selon la langue
            error_messages = {
                'fr': f"Je n'ai pas compris la commande '{command_text}'. Voulez-vous l'ajouter aux commandes personnalisées ? Dites 'aide' pour voir les commandes disponibles.",
                'en': f"I didn't understand the command '{command_text}'. Would you like to add it to custom commands? Say 'help' to see available commands.",
                'es': f"No entendí el comando '{command_text}'. ¿Quieres añadirlo a los comandos personalizados? Di 'ayuda' para ver los comandos disponibles.",
                'nl': f"Ik begreep het commando '{command_text}' niet. Wil je het toevoegen aan aangepaste commando's? Zeg 'help' om beschikbare commando's te zien."
            }
            
            # Déterminer la langue de l'utilisateur
            user_lang = 'fr'  # Par défaut
            if user and hasattr(user, 'native_language'):
                user_lang = user.native_language.lower()[:2]
            
            error_message = error_messages.get(user_lang, error_messages['fr'])
            
            return {
                'success': False,
                'action': 'unknown',
                'params': {'original_command': command_text},
                'response': error_message,
                'command': command_text_lower,
                'learn_suggestion': True
            }
            
        except Exception as e:
            logger.error(f"Error processing voice command '{command_text}': {e}")
            return {
                'success': False,
                'action': 'error',
                'params': {'error': str(e)},
                'response': 'Une erreur est survenue lors du traitement de la commande',
                'command': command_text,
                'confidence': 0.0
            }
    
    def _build_user_context(self, user) -> Dict[str, Any]:
        """Construit le contexte utilisateur pour l'IA"""
        if not user:
            return {}
        
        try:
            context = {
                'user_id': user.id,
                'username': user.username,
                'native_language': getattr(user, 'native_language', 'FR'),
                'target_language': getattr(user, 'target_language', 'EN'),
                'language_level': getattr(user, 'language_level', 'A1'),
                'is_authenticated': user.is_authenticated,
                'preferences': {}
            }
            
            # Ajouter les préférences vocales si disponibles
            try:
                from .models.vocal_models import VoicePreference
                voice_pref = VoicePreference.objects.filter(user=user).first()
                if voice_pref:
                    context['preferences'].update({
                        'tts_enabled': voice_pref.tts_enabled,
                        'conversation_mode': voice_pref.conversation_mode,
                        'preferred_voice_speed': voice_pref.preferred_voice_speed
                    })
            except Exception:
                pass  # Les préférences vocales ne sont pas critiques
            
            logger.debug(f"Built user context for {user.username}: {context}")
            return context
            
        except Exception as e:
            logger.warning(f"Error building user context: {e}")
            return {'user_id': getattr(user, 'id', None), 'username': getattr(user, 'username', 'Unknown')}

    def requires_confirmation(self, action: str) -> bool:
        """Détermine si une action nécessite une confirmation"""
        dangerous_actions = [
            'logout', 'delete_account', 'reset_data', 
            'clear_history', 'delete_all_notes'
        ]
        return action in dangerous_actions
    
    def learn_new_command(self, trigger_phrase: str, action: str, params: dict, response: str, user=None):
        """Apprend une nouvelle commande personnalisée"""
        try:
            from .models.vocal_models import VoiceCommand
            
            if user:
                # Sauvegarder en base de données
                voice_command, created = VoiceCommand.objects.get_or_create(
                    user=user,
                    trigger_phrase=trigger_phrase.lower(),
                    defaults={
                        'action_type': action,
                        'action_params': params,
                        'is_active': True
                    }
                )
                
                if created:
                    # Ajouter à la session courante
                    self.voice_commands[trigger_phrase.lower()] = {
                        'action': action,
                        'params': params,
                        'response': response
                    }
                    return True
                    
            return False
        except Exception as e:
            logger.error(f"Error learning new command: {e}")
            return False
    
    def get_user_custom_commands(self, user):
        """Récupère les commandes personnalisées de l'utilisateur"""
        try:
            from .models.vocal_models import VoiceCommand
            
            if user:
                custom_commands = VoiceCommand.objects.filter(
                    user=user, 
                    is_active=True
                )
                
                commands_dict = {}
                for cmd in custom_commands:
                    commands_dict[cmd.trigger_phrase] = {
                        'action': cmd.action_type,
                        'params': cmd.action_params,
                        'response': f"Exécution de votre commande personnalisée: {cmd.trigger_phrase}"
                    }
                    
                return commands_dict
        except Exception as e:
            logger.error(f"Error getting user custom commands: {e}")
            
        return {}
    
    def _normalize_command_text(self, text: str) -> str:
        """Normalise le texte pour améliorer la correspondance"""
        if not text:
            return ""
        
        # Dictionnaire de synonymes et variantes multilingues
        synonyms_map = {
            # Navigation mixte FR-EN
            'dashboard': ['tableau de bord', 'accueil', 'home'],
            'settings': ['paramètres', 'configuration', 'config'],
            'profile': ['profil'],
            'notes': ['note', 'carnet'],
            'revision': ['révision', 'révisions'],
            'quiz': ['quizz', 'test'],
            'learning': ['apprentissage', 'cours', 'leçon'],
            'community': ['communauté'],
            'chat': ['conversation', 'discuter'],
            
            # Verbes d'action
            'aller': ['go', 'navigate', 'ouvrir', 'open'],
            'activer': ['enable', 'activate'],
            'désactiver': ['disable', 'deactivate'],
            
            # Thèmes
            'dark': ['sombre', 'noir'],
            'light': ['clair', 'blanc'],
            'mode': ['thème', 'theme'],
        }
        
        normalized = text.lower().strip()
        
        # Remplacer les synonymes
        for canonical, variants in synonyms_map.items():
            for variant in variants:
                if variant in normalized:
                    normalized = normalized.replace(variant, canonical)
        
        return normalized
    
    def _semantic_match(self, input_text: str) -> Optional[Dict[str, Any]]:
        """Correspondance sémantique avancée pour les commandes non reconnues"""
        if not input_text:
            return None
        
        input_lower = input_text.lower().strip()
        
        # Patterns de navigation avec mots-clés flexibles
        navigation_patterns = {
            'dashboard': {
                'keywords': ['dashboard', 'tableau', 'bord', 'accueil', 'home', 'principal'],
                'action': 'navigate',
                'params': {'url': '/dashboard/', 'page': 'dashboard'},
                'response': 'Navigation vers le tableau de bord'
            },
            'settings': {
                'keywords': ['settings', 'paramètres', 'configuration', 'config', 'réglages'],
                'action': 'navigate', 
                'params': {'url': '/settings/', 'page': 'settings'},
                'response': 'Navigation vers les paramètres'
            },
            'notes': {
                'keywords': ['notes', 'note', 'carnet', 'notebook', 'écrire'],
                'action': 'navigate',
                'params': {'url': '/notebook/', 'page': 'notebook'},
                'response': 'Navigation vers les notes'
            },
            'quiz': {
                'keywords': ['quiz', 'quizz', 'test', 'questionnaire', 'évaluation'],
                'action': 'navigate',
                'params': {'url': '/quizz/', 'page': 'quizz'},
                'response': 'Navigation vers les quiz'
            },
            'community': {
                'keywords': ['communauté', 'community', 'social', 'amis', 'friends'],
                'action': 'navigate',
                'params': {'url': '/community/', 'page': 'community'},
                'response': 'Navigation vers la communauté'
            }
        }
        
        # Actions de thème
        theme_patterns = {
            'dark_mode': {
                'keywords': ['dark', 'sombre', 'noir', 'mode sombre'],
                'action': 'toggle_theme',
                'params': {'theme': 'dark'},
                'response': 'Mode sombre activé'
            },
            'light_mode': {
                'keywords': ['light', 'clair', 'blanc', 'mode clair'],
                'action': 'toggle_theme', 
                'params': {'theme': 'light'},
                'response': 'Mode clair activé'
            }
        }
        
        # Vérifier tous les patterns
        all_patterns = {**navigation_patterns, **theme_patterns}
        
        for pattern_name, pattern_data in all_patterns.items():
            keywords = pattern_data['keywords']
            
            # Compter les mots-clés correspondants
            matches = sum(1 for keyword in keywords if keyword in input_lower)
            
            # Si au moins un mot-clé correspond
            if matches > 0:
                return {
                    'success': True,
                    'action': pattern_data['action'],
                    'params': pattern_data['params'],
                    'response': pattern_data['response'],
                    'command': input_text,
                    'confidence': min(0.8, matches / len(keywords) + 0.3),
                    'matched_semantic': True,
                    'pattern': pattern_name
                }
        
        return None
    
    def _fuzzy_match(self, input_text: str, command_phrase: str) -> bool:
        """Effectue une correspondance approximative entre le texte d'entrée et une phrase de commande"""
        if not input_text or not command_phrase:
            return False
        
        # Normaliser les textes avec synonymes
        normalized_input = self._normalize_command_text(input_text)
        normalized_command = self._normalize_command_text(command_phrase)
        
        # Vérifier correspondance exacte d'abord
        if normalized_input == normalized_command:
            return True
        
        # Vérifier si la commande est contenue dans l'entrée
        if normalized_command in normalized_input or normalized_input in normalized_command:
            return True
        
        # Analyse par mots
        input_words = set(word for word in normalized_input.split() if len(word) > 1)
        command_words = set(word for word in normalized_command.split() if len(word) > 1)
        
        if not command_words:
            return False
        
        # Si au moins 60% des mots de la commande sont présents dans l'entrée (abaissé pour plus de flexibilité)
        intersection = input_words.intersection(command_words)
        match_ratio = len(intersection) / len(command_words)
        
        return match_ratio >= 0.6
    
    def get_available_commands(self, language: str = 'fr') -> list:
        """Retourne la liste des commandes disponibles"""
        return list(self.voice_commands.keys())
    
    def get_commands_for_user_language(self, user):
        """Retourne les commandes dans la langue de l'utilisateur"""
        if user and hasattr(user, 'native_language'):
            user_language = user.native_language
            logger.info(f"User {user.username} has native_language: '{user_language}'")
            return self._get_commands_for_language(user_language)
        else:
            logger.info(f"User {user.username if user else 'Anonymous'} has no native_language, using French")
            return self._get_commands_for_language('fr')
    
    def add_custom_command(self, trigger_phrase: str, action: str, params: dict, response: str):
        """Ajoute une commande personnalisée"""
        self.voice_commands[trigger_phrase.lower()] = {
            'action': action,
            'params': params,
            'response': response
        }

# Instance globale du service
voice_service = VoiceAssistantService()

# TTS désactivé - utiliser Web Speech API côté client
TTS_AVAILABLE = False
engine = None

def get_language_code(language):
    """
    Convertit le code de langue de l'app vers le code Google Speech Recognition
    """
    if not language:
        return 'en-US'
    
    # Utiliser le mapping du service pour cohérence
    try:
        service_instance = voice_service if 'voice_service' in globals() else VoiceAssistantService()
        language_mapping = service_instance.get_language_mapping()
        
        # Nettoyer et normaliser la langue d'entrée
        clean_language = str(language).lower().strip()
        
        # Chercher une correspondance exacte d'abord
        if clean_language in language_mapping:
            return language_mapping[clean_language]
        
        # Chercher par code de langue de base (ex: 'en' depuis 'en-US')
        base_language = clean_language.split('-')[0]
        if base_language in language_mapping:
            return language_mapping[base_language]
        
        # Fallback par défaut
        return 'en-US'
    except Exception as e:
        logger.error(f"Error getting language code for '{language}': {e}")
        return 'en-US'

def set_voice_language(language_code):
    """
    Configure la langue du moteur TTS
    """
    voices = engine.getProperty('voices')
    for voice in voices:
        if language_code[:2] in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break

def speak(text, language='en'):
    """
    Fait parler le texte dans la langue spécifiée
    """
    if not TTS_AVAILABLE or not engine:
        return {"error": "TTS not available", "text": text}
    
    try:
        set_voice_language(language)
        engine.say(text)
        engine.runAndWait()
        return {"success": True, "text": text}
    except Exception as e:
        logger.error(f"Error in speak function: {e}")
        return {"error": f"TTS error: {str(e)}", "text": text}

def listen(user=None, language=None):
    """
    Écoute et reconnaît la parole
    """
    r = sr.Recognizer()
    
    # Déterminer la langue à utiliser
    try:
        if language:
            lang_code = get_language_code(language)
        elif user and hasattr(user, 'native_language'):
            lang_code = get_language_code(user.native_language)
        else:
            lang_code = 'en-US'
    except Exception as e:
        logger.error(f"Error determining language: {e}")
        lang_code = 'en-US'
    
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        
        command = r.recognize_google(audio, language=lang_code)
        return command
    
    except sr.UnknownValueError:
        error_msg = "Je n'ai pas compris" if lang_code.startswith('fr') else "I didn't understand"
        speak(error_msg, language=lang_code[:2])
        return ''
    except sr.RequestError as e:
        error_msg = 'Service non disponible' if lang_code.startswith('fr') else 'Service unavailable'
        speak(error_msg, language=lang_code[:2])
        logger.error(f"Speech recognition service error: {e}")
        return ''
    except Exception as e:
        logger.error(f"Unexpected error in listen(): {e}")
        return ''