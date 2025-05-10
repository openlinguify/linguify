import requests
import logging
import os
import json
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .ai_providers import AIProvider

logger = logging.getLogger(__name__)

# AI Provider peut être configuré dans settings.py avec AI_PROVIDER
# Options disponibles: 'openai', 'huggingface', 'ollama', 'simulator'
AI_PROVIDER_NAME = getattr(settings, 'AI_PROVIDER', os.environ.get('AI_PROVIDER', 'simulator'))

# Initialiser le provider d'IA
ai_provider = AIProvider.get_provider(AI_PROVIDER_NAME)
logger.info(f"Using AI provider: {AI_PROVIDER_NAME}")

if ai_provider.is_available():
    logger.info(f"AI provider {AI_PROVIDER_NAME} is available and configured")
else:
    logger.warning(f"AI provider {AI_PROVIDER_NAME} is not properly configured or not available.")

# Vous pouvez remplacer cette fonction par une intégration avec OpenAI, Azure, ou un autre service d'IA
def generate_ai_response(conversation, user_message):
    """
    Génère une réponse AI basée sur la conversation et le message utilisateur.
    
    Args:
        conversation: L'objet AIConversation
        user_message: Le contenu du message de l'utilisateur
        
    Returns:
        dict: Un dictionnaire avec la réponse et l'analyse
    """
    try:
        # Construction du contexte pour l'IA
        # Récupérer les messages précédents (max 10 derniers)
        previous_messages = conversation.messages.order_by('-created_at')[:10]
        
        # Inverser pour avoir l'ordre chronologique
        previous_messages = list(reversed(previous_messages))
        
        # Construire le contexte de la conversation
        conversation_context = [
            {"role": "system", "content": f"You are a language tutor for {conversation.language}. {conversation.ai_persona}"}
        ]
        
        # Ajouter le contexte du sujet
        topic = conversation.topic
        if topic:
            conversation_context.append({
                "role": "system", 
                "content": f"The topic of this conversation is: {topic.name}. {topic.context}"
            })
            
            # Ajouter l'exemple de conversation si disponible
            if topic.example_conversation:
                conversation_context.append({
                    "role": "system", 
                    "content": f"Here's how the conversation should flow: {topic.example_conversation}"
                })
        
        # Ajouter une instruction pour fournir des corrections et du feedback
        conversation_context.append({
            "role": "system", 
            "content": (
                "You should respond conversationally, but also provide helpful corrections "
                "when the user makes grammar or vocabulary mistakes. "
                "Keep your responses friendly, engaging, and educational. "
                f"Always respond in {conversation.language}."
            )
        })
        
        # Ajouter les messages précédents comme contexte
        for msg in previous_messages:
            role = "assistant" if msg.message_type == "ai" else "user"
            if msg.message_type != "system":  # Skip system messages
                conversation_context.append({
                    "role": role,
                    "content": msg.content
                })
        
        # Ajouter le message actuel de l'utilisateur
        conversation_context.append({
            "role": "user",
            "content": user_message
        })
        
        # Analyse de grammaire et de vocabulaire
        grammar_analysis = analyze_grammar(user_message, conversation.language)
        vocabulary_level = analyze_vocabulary(user_message, conversation.language)
        
        # Utiliser le provider AI configuré
        if ai_provider.is_available():
            try:
                logger.info(f"Calling {AI_PROVIDER_NAME} provider for conversation {conversation.id}")
                
                # Appel au provider AI
                ai_response = ai_provider.generate_response(
                    messages=conversation_context,
                    language=conversation.language,
                    max_tokens=500
                )
                
                if ai_response:
                    logger.info(f"{AI_PROVIDER_NAME} response received for conversation {conversation.id}")
                    
                    return {
                        "response": ai_response,
                        "grammar_analysis": json.dumps(grammar_analysis) if grammar_analysis else None,
                        "vocabulary_level": vocabulary_level
                    }
                else:
                    # Si le provider répond mais avec une erreur, fallback sur la simulation
                    logger.warning(f"{AI_PROVIDER_NAME} returned empty response, falling back to simulator")
                    response = simulate_ai_response(user_message, conversation.language, grammar_analysis)
            except Exception as ai_error:
                logger.error(f"Error with {AI_PROVIDER_NAME} provider: {str(ai_error)}")
                logger.warning("Falling back to simulated response")
                # Fallback sur la réponse simulée en cas d'erreur
                response = simulate_ai_response(user_message, conversation.language, grammar_analysis)
        else:
            # Si le provider n'est pas disponible, utiliser la réponse simulée
            logger.info(f"{AI_PROVIDER_NAME} provider not available, using simulator")
            response = simulate_ai_response(user_message, conversation.language, grammar_analysis)
        
        return {
            "response": response,
            "grammar_analysis": json.dumps(grammar_analysis) if grammar_analysis else None,
            "vocabulary_level": vocabulary_level
        }
    
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return {
            "response": _("I'm sorry, I'm having trouble understanding. Could you try again or rephrase?"),
            "grammar_analysis": None,
            "vocabulary_level": None
        }

def analyze_grammar(text, language):
    """Simuler une analyse grammaticale basique."""
    # Cette fonction est un placeholder - dans une implémentation réelle, 
    # vous appelleriez un service de NLP ou une API de correction grammaticale
    common_errors = {
        'en': {
            'is/are': r'\b(he|she|it)\s+are\b',
            'a/an': r'\ban\s+[^aeiou]',
            'tense': r'\bhave\s+went\b'
        },
        'fr': {
            'gender': r'\ble\s+[a-z]+e\b',
            'subjonctif': r'\b(il faut que)\s+[a-z]+e\b' 
        },
        'es': {
            'ser/estar': r'\bestoy\s+[a-z]+o\b',
            'subjuntivo': r'\bcuando\s+[a-z]+o\b'
        }
    }
    
    language_errors = common_errors.get(language, {})
    found_errors = []
    
    # Analyse simplifiée pour l'exemple
    if language == 'en' and 'i am go' in text.lower():
        found_errors.append({
            "error": "incorrect verb tense",
            "correction": "I am going",
            "explanation": "Use present continuous (am + verb-ing) for ongoing actions."
        })
    elif language == 'fr' and 'je suis alle' in text.lower():
        found_errors.append({
            "error": "missing accent",
            "correction": "Je suis allé",
            "explanation": "Past participle for masculine requires an accent: allé"
        })
    
    return found_errors if found_errors else None

def analyze_vocabulary(text, language):
    """Évaluer le niveau de vocabulaire utilisé."""
    word_count = len(text.split())
    
    # Logique simplifiée pour l'exemple
    if word_count < 5:
        return "beginner"
    elif word_count < 15:
        return "intermediate"
    else:
        return "advanced"

def simulate_ai_response(user_message, language, grammar_analysis):
    """Génère une réponse simulée pour démonstration."""
    
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
    response = language_responses[index]
    
    # Si des erreurs grammaticales ont été détectées, ajouter une correction
    if grammar_analysis and len(grammar_analysis) > 0:
        error = grammar_analysis[0]
        
        correction_templates = {
            'en': "\n\nBy the way, I noticed a small grammar point: '{}' would be better as '{}'. {}",
            'fr': "\n\nAu fait, j'ai remarqué un petit point de grammaire: '{}' serait mieux comme '{}'. {}",
            'es': "\n\nPor cierto, noté un pequeño punto gramatical: '{}' sería mejor como '{}'. {}"
        }
        
        template = correction_templates.get(language, correction_templates['en'])
        correction = template.format(
            error.get('error', ''),
            error.get('correction', ''),
            error.get('explanation', '')
        )
        
        response += correction
    
    return response