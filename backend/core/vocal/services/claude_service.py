"""
Service Claude API intégré pour l'assistant vocal Linguify
"""
import logging
import json
from typing import Dict, Any, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class ClaudeService:
    """Service pour interagir avec l'API Claude d'Anthropic"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'CLAUDE_API_KEY', None)
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-haiku-20240307"  # Modèle rapide pour les commandes vocales
        
    def is_available(self) -> bool:
        """Vérifie si le service Claude est disponible"""
        return bool(self.api_key)
    
    def analyze_voice_command(self, user_input: str, user_context: Dict) -> Dict[str, Any]:
        """
        Analyse une commande vocale avec Claude pour extraire l'intention et les actions
        
        Args:
            user_input: Commande vocale de l'utilisateur
            user_context: Contexte utilisateur (niveau, langue, etc.)
            
        Returns:
            Dict avec l'analyse Claude et les actions suggérées
        """
        
        if not self.is_available():
            return self._fallback_analysis(user_input, user_context)
        
        try:
            prompt = self._build_analysis_prompt(user_input, user_context)
            response = self._call_claude_api(prompt)
            
            return self._parse_claude_response(response, user_input)
            
        except Exception as e:
            logger.error(f"Erreur Claude API: {e}")
            return self._fallback_analysis(user_input, user_context)
    
    def _build_analysis_prompt(self, user_input: str, user_context: Dict) -> str:
        """Construit le prompt pour Claude"""
        
        # Extraire les informations utilisateur
        native_language = user_context.get('native_language', 'FR')
        target_language = user_context.get('target_language', 'EN')
        language_level = user_context.get('language_level', 'A1')
        username = user_context.get('username', 'utilisateur')
        
        return f"""Tu es l'assistant vocal intelligent de Linguify, une plateforme d'apprentissage des langues.

CONTEXTE UTILISATEUR:
- Nom: {username}
- Langue native: {native_language}
- Langue cible: {target_language} 
- Niveau: {language_level}

COMMANDE UTILISATEUR: "{user_input}"

ACTIONS DISPONIBLES DANS LINGUIFY:
1. NAVIGATION: aller à dashboard, notes, revision, quiz, learning, community, conversation, profile, settings
2. FLASHCARDS: créer flashcard, ajouter au deck, créer deck de révision
3. INFORMATIONS: progrès utilisateur, statistiques, recommandations
4. MOTIVATION: encouragement, conseil, support
5. CONTRÔLES: mode sombre/clair, TTS, préférences

INSTRUCTIONS:
1. Analyse l'intention de l'utilisateur
2. Identifie l'action Linguify appropriée
3. Extrais les paramètres nécessaires (mots à apprendre, deck cible, etc.)
4. Réponds en JSON avec cette structure EXACTE:

{{
    "intention": "description_claire_de_l_intention",
    "action": "nom_action_linguify",
    "parametres": {{
        "mots_a_apprendre": ["mot1", "mot2"],
        "deck_cible": "nom_du_deck",
        "front_text": "texte_recto",
        "back_text": "texte_verso",
        "url": "/url/navigation",
        "autres_params": "valeur"
    }},
    "reponse_utilisateur": "réponse naturelle à dire à l'utilisateur",
    "actions_suggerees": [
        {{"text": "Action 1", "action": "navigate", "params": {{"url": "/revision/"}}}}
    ],
    "confiance": 0.9
}}

EXEMPLES:
- "créer une flashcard avec bonjour et hello" → action: "create_flashcard"
- "ajouter vocabulaire important" → action: "extract_and_create_flashcards"  
- "aller réviser" → action: "navigate"
- "comment je progresse" → action: "get_user_stats"

Réponds UNIQUEMENT en JSON valide."""

    def _call_claude_api(self, prompt: str) -> str:
        """Appelle l'API Claude (simulation pour l'instant)"""
        
        # TODO: Remplacer par le vrai appel API Claude
        # Pour l'instant, simulation intelligente basée sur le prompt
        
        if "flashcard" in prompt.lower() or "vocabulaire" in prompt.lower():
            return self._simulate_flashcard_response(prompt)
        elif "progresse" in prompt.lower() or "progrès" in prompt.lower():
            return self._simulate_progress_response()
        elif "aller" in prompt.lower() or "navigation" in prompt.lower():
            return self._simulate_navigation_response(prompt)
        else:
            return self._simulate_general_response(prompt)
    
    def _simulate_flashcard_response(self, prompt: str) -> str:
        """Simule une réponse Claude pour les flashcards"""
        return json.dumps({
            "intention": "Créer des flashcards pour apprendre du vocabulaire",
            "action": "create_flashcard",
            "parametres": {
                "front_text": "bonjour",
                "back_text": "hello",
                "deck_cible": "Vocabulaire quotidien",
                "front_language": "fr",
                "back_language": "en"
            },
            "reponse_utilisateur": "J'ai créé une flashcard avec 'bonjour' → 'hello' dans votre deck de vocabulaire quotidien.",
            "actions_suggerees": [
                {"text": "Aller réviser", "action": "navigate", "params": {"url": "/revision/"}},
                {"text": "Créer plus de cartes", "action": "create_flashcard", "params": {"deck_cible": "Vocabulaire quotidien"}}
            ],
            "confiance": 0.95
        })
    
    def _simulate_progress_response(self) -> str:
        """Simule une réponse Claude pour les progrès"""
        return json.dumps({
            "intention": "Consulter les progrès d'apprentissage",
            "action": "get_user_stats",
            "parametres": {
                "stats_type": "learning_progress"
            },
            "reponse_utilisateur": "Voyons vos progrès d'apprentissage...",
            "actions_suggerees": [
                {"text": "Voir détails", "action": "navigate", "params": {"url": "/profile/"}},
                {"text": "Continuer révision", "action": "navigate", "params": {"url": "/revision/"}}
            ],
            "confiance": 0.9
        })
    
    def _simulate_navigation_response(self, prompt: str) -> str:
        """Simule une réponse Claude pour la navigation"""
        # Extraire la destination du prompt
        if "revision" in prompt.lower():
            url = "/revision/"
            destination = "révision"
        elif "notes" in prompt.lower():
            url = "/notebook/"
            destination = "notes"
        elif "dashboard" in prompt.lower():
            url = "/dashboard/"
            destination = "tableau de bord"
        else:
            url = "/dashboard/"
            destination = "tableau de bord"
        
        return json.dumps({
            "intention": f"Naviguer vers {destination}",
            "action": "navigate",
            "parametres": {
                "url": url,
                "page": destination
            },
            "reponse_utilisateur": f"Navigation vers {destination}...",
            "actions_suggerees": [],
            "confiance": 0.85
        })
    
    def _simulate_general_response(self, prompt: str) -> str:
        """Simulation générale pour autres demandes"""
        return json.dumps({
            "intention": "Demande d'assistance générale",
            "action": "ai_assistance",
            "parametres": {},
            "reponse_utilisateur": "Je peux vous aider avec Linguify. Essayez 'créer une flashcard' ou 'aller réviser'.",
            "actions_suggerees": [
                {"text": "Révision", "action": "navigate", "params": {"url": "/revision/"}},
                {"text": "Mes progrès", "action": "get_user_stats", "params": {"stats_type": "learning_progress"}}
            ],
            "confiance": 0.7
        })
    
    def _parse_claude_response(self, response: str, original_input: str) -> Dict[str, Any]:
        """Parse la réponse JSON de Claude"""
        try:
            data = json.loads(response)
            
            return {
                'success': True,
                'intention': data.get('intention'),
                'action': data.get('action'),
                'params': data.get('parametres', {}),
                'response': data.get('reponse_utilisateur'),
                'suggested_actions': data.get('actions_suggerees', []),
                'confidence': data.get('confiance', 0.8),
                'ai_enhanced': True,
                'claude_used': True,
                'original_input': original_input
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing réponse Claude: {e}")
            return self._fallback_analysis(original_input, {})
    
    def _fallback_analysis(self, user_input: str, user_context: Dict) -> Dict[str, Any]:
        """Analyse de fallback si Claude n'est pas disponible"""
        
        input_lower = user_input.lower()
        
        # Patterns améliorés pour flashcards en français
        flashcard_keywords = ['flashcard', 'carte', 'vocabulaire', 'créer', 'ajouter', 'révision', 'apprendre', 'mémoriser']
        
        if any(word in input_lower for word in flashcard_keywords):
            # Extraire les mots de la commande pour créer la flashcard
            front_text, back_text = self._extract_words_from_command(user_input)
            
            return {
                'success': True,
                'intention': 'Créer du contenu de révision',
                'action': 'create_flashcard',
                'params': {
                    'front_text': front_text,
                    'back_text': back_text,
                    'deck_cible': 'Vocabulaire IA'
                },
                'response': f'Je vais créer une flashcard avec "{front_text}" → "{back_text}"',
                'suggested_actions': [
                    {'text': 'Aller réviser', 'action': 'navigate', 'params': {'url': '/revision/'}}
                ],
                'confidence': 0.8,
                'ai_enhanced': True,
                'claude_used': False
            }
        
        return {
            'success': False,
            'intention': 'Non reconnu',
            'action': 'unknown',
            'params': {},
            'response': f"Je n'ai pas bien compris '{user_input}'. Pouvez-vous reformuler ?",
            'suggested_actions': [],
            'confidence': 0.1,
            'ai_enhanced': False,
            'claude_used': False
        }
    
    def _extract_words_from_command(self, command: str) -> tuple[str, str]:
        """Extrait les mots à apprendre d'une commande vocale"""
        
        command_lower = command.lower()
        
        # Patterns pour extraire les mots
        import re
        
        # Pattern "créer une flashcard avec X et Y"
        pattern1 = r'(?:créer|faire|ajouter).*(?:flashcard|carte).*avec\s+([^,\s]+).*et\s+([^,\s]+)'
        match1 = re.search(pattern1, command_lower)
        if match1:
            return match1.group(1).strip(), match1.group(2).strip()
        
        # Pattern "X et Y" simple
        pattern2 = r'([a-zA-ZÀ-ÿ]+)\s+et\s+([a-zA-ZÀ-ÿ]+)'
        match2 = re.search(pattern2, command_lower)
        if match2:
            return match2.group(1).strip(), match2.group(2).strip()
        
        # Pattern avec mots courants français-anglais
        common_pairs = {
            'bonjour': 'hello',
            'merci': 'thank you',
            'apprendre': 'learn',
            'important': 'important',
            'vocabulaire': 'vocabulary'
        }
        
        for fr_word, en_word in common_pairs.items():
            if fr_word in command_lower:
                return fr_word, en_word
        
        # Fallback
        return 'mot', 'word'

# Instance globale du service Claude
claude_service = ClaudeService()