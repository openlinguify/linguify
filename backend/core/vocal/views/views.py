from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import base64
import io
try:
    import speech_recognition as sr
except ImportError:
    sr = None
from ..serializers import (
    TextToSpeechSerializer, 
    SpeechToTextSerializer,
    TranscriptionResultSerializer
)
from ..services import voice_service
import time


@api_view(['GET'])
def api_root(request):
    """
    Root endpoint for the Vocal API
    """
    return Response({
        'message': 'Welcome to the Vocal API',
        'version': '1.0',
        'endpoints': {
            'root': '/api/v1/vocal/',
            'speech-to-text': '/api/v1/vocal/speech-to-text/',
            'text-to-speech': '/api/v1/vocal/text-to-speech/',
            'voice-command': '/api/v1/vocal/voice-command/',
            'commands': '/api/v1/vocal/commands/',
            'languages': '/api/v1/vocal/languages/',
        }
    }, status=status.HTTP_200_OK)


class SpeechToTextView(APIView):
    """
    Convertit l'audio en texte
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if sr is None:
            return Response({
                'error': 'Speech recognition not available. Please install speech_recognition package.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        serializer = SpeechToTextSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Décoder l'audio base64
            audio_data = base64.b64decode(serializer.validated_data['audio_data'])
            language = serializer.validated_data.get('language', 'en')
            
            # Utiliser speech_recognition
            r = sr.Recognizer()
            with io.BytesIO(audio_data) as audio_file:
                with sr.AudioFile(audio_file) as source:
                    audio = r.record(source)
                    
            # Reconnaissance vocale
            from ..services import get_language_code
            lang_code = get_language_code(language)
            text = r.recognize_google(audio, language=lang_code)
            
            result = TranscriptionResultSerializer({
                'text': text,
                'language': language,
                'success': True
            })
            
            return Response(result.data, status=status.HTTP_200_OK)
            
        except sr.UnknownValueError:
            return Response({
                'success': False,
                'error': 'Could not understand audio'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TextToSpeechView(APIView):
    """
    Convertit le texte en voix (retourne les paramètres pour TTS côté client)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = TextToSpeechSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Pour l'instant, on retourne juste les paramètres
        # Le TTS sera fait côté client avec Web Speech API
        return Response({
            'text': serializer.validated_data['text'],
            'language': serializer.validated_data['language'],
            'voice': serializer.validated_data.get('voice'),
            'success': True
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supported_languages(request):
    """
    Retourne les langues supportées
    """
    languages = {
        'en': 'English',
        'fr': 'Français',
        'es': 'Español',
        'de': 'Deutsch',
        'it': 'Italiano',
        'pt': 'Português',
        'nl': 'Nederlands',
        'ru': 'Русский',
        'ja': '日本語',
        'zh': '中文',
        'ar': 'العربية',
    }
    
    return Response({
        'languages': languages,
        'default': 'en'
    }, status=status.HTTP_200_OK)


class VoiceCommandView(APIView):
    """
    Traite les commandes vocales et retourne les actions à effectuer
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Traite une commande vocale"""
        command_text = request.data.get('command', '').strip()
        
        if not command_text:
            return Response({
                'success': False,
                'error': 'No command provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_time = time.time()
            
            # Traiter la commande avec le service vocal
            result = voice_service.process_voice_command(command_text, request.user)
            
            # Calculer le temps de réponse
            response_time = (time.time() - start_time) * 1000  # en millisecondes
            result['response_time'] = round(response_time, 2)
            result['user'] = request.user.username
            
            # Log de l'interaction (vous pouvez sauvegarder en DB plus tard)
            print(f"Voice Command - User: {request.user.username}, Command: '{command_text}', Success: {result['success']}, Time: {response_time}ms")
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'action': 'error',
                'response': 'Une erreur est survenue lors du traitement de votre commande.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VoiceCommandsListView(APIView):
    """
    Retourne la liste des commandes vocales disponibles
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Récupère la liste des commandes disponibles selon la langue de l'utilisateur"""
        try:
            # Récupérer les commandes dans la langue de l'utilisateur
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"VoiceCommandsListView: User {request.user.username} requesting commands")
            logger.info(f"User native_language: {getattr(request.user, 'native_language', 'Not set')}")
            
            user_commands = voice_service.get_commands_for_user_language(request.user)
            logger.info(f"Retrieved {len(user_commands)} commands for user")
            
            # Organiser les commandes par catégorie
            categorized_commands = {
                'navigation': [],
                'learning': [],
                'voice_control': [],
                'help': []
            }
            
            for command, command_data in user_commands.items():
                action = command_data['action']
                
                if action in ['navigate']:
                    category = 'navigation'
                elif action in ['start_lesson', 'start_quiz', 'review_vocabulary', 'practice_pronunciation']:
                    category = 'learning'
                elif action in ['enable_tts', 'disable_tts', 'change_speed', 'toggle_theme']:
                    category = 'voice_control'
                else:
                    category = 'help'
                
                categorized_commands[category].append({
                    'command': command,
                    'action': action,
                    'description': command_data['response']
                })
            
            return Response({
                'success': True,
                'commands': categorized_commands,
                'total_commands': len(user_commands),
                'user_language': getattr(request.user, 'native_language', 'fr')
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SpeechToTextWithCommandView(APIView):
    """
    Combine la reconnaissance vocale avec le traitement de commandes
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Convertit l'audio en texte puis traite comme commande"""
        if sr is None:
            return Response({
                'error': 'Speech recognition not available. Please install speech_recognition package.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        try:
            # D'abord, faire la reconnaissance vocale
            stt_serializer = SpeechToTextSerializer(data=request.data)
            if not stt_serializer.is_valid():
                return Response(stt_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Décoder l'audio base64
            audio_data = base64.b64decode(stt_serializer.validated_data['audio_data'])
            language = stt_serializer.validated_data.get('language', 'fr')
            
            # Reconnaissance vocale
            r = sr.Recognizer()
            with io.BytesIO(audio_data) as audio_file:
                with sr.AudioFile(audio_file) as source:
                    audio = r.record(source)
                    
            from ..services import get_language_code
            lang_code = get_language_code(language)
            recognized_text = r.recognize_google(audio, language=lang_code)
            
            # Traiter comme commande vocale
            start_time = time.time()
            command_result = voice_service.process_voice_command(recognized_text, request.user)
            response_time = (time.time() - start_time) * 1000
            
            # Combiner les résultats
            return Response({
                'transcription': {
                    'text': recognized_text,
                    'language': language,
                    'success': True
                },
                'command': {
                    **command_result,
                    'response_time': round(response_time, 2)
                },
                'overall_success': True
            }, status=status.HTTP_200_OK)
            
        except sr.UnknownValueError:
            return Response({
                'transcription': {
                    'success': False,
                    'error': 'Could not understand audio'
                },
                'command': {
                    'success': False,
                    'response': 'Je n\'ai pas compris votre commande vocale.'
                },
                'overall_success': False
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'transcription': {
                    'success': False,
                    'error': str(e)
                },
                'command': {
                    'success': False,
                    'response': 'Une erreur est survenue lors du traitement.'
                },
                'overall_success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LearnCommandView(APIView):
    """
    Permet d'apprendre de nouvelles commandes vocales personnalisées
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Apprend une nouvelle commande vocale"""
        trigger_phrase = request.data.get('trigger_phrase', '').strip()
        action = request.data.get('action', '').strip()
        params = request.data.get('params', {})
        response_text = request.data.get('response', '')
        
        if not trigger_phrase or not action:
            return Response({
                'success': False,
                'error': 'trigger_phrase and action are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            success = voice_service.learn_new_command(
                trigger_phrase=trigger_phrase,
                action=action,
                params=params,
                response=response_text,
                user=request.user
            )
            
            if success:
                return Response({
                    'success': True,
                    'message': f'Command "{trigger_phrase}" learned successfully',
                    'trigger_phrase': trigger_phrase,
                    'action': action
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': 'Failed to learn command - command may already exist'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VoicePreferencesView(APIView):
    """
    Gère les préférences vocales de l'utilisateur
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Récupère les préférences vocales de l'utilisateur"""
        try:
            from ..models import VoicePreference
            
            preference, created = VoicePreference.objects.get_or_create(
                user=request.user,
                defaults={
                    'tts_enabled': True,
                    'voice_commands_enabled': True,
                    'preferred_voice_speed': 'normal',
                    'auto_listen': False,
                    'conversation_mode': False
                }
            )
            
            return Response({
                'success': True,
                'preferences': {
                    'tts_enabled': preference.tts_enabled,
                    'voice_commands_enabled': preference.voice_commands_enabled,
                    'preferred_voice_speed': preference.preferred_voice_speed,
                    'preferred_voice_pitch': preference.preferred_voice_pitch,
                    'auto_listen': preference.auto_listen,
                    'noise_suppression': preference.noise_suppression,
                    'sensitivity': preference.sensitivity,
                    'conversation_mode': preference.conversation_mode,
                    'pronunciation_feedback': preference.pronunciation_feedback
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Met à jour les préférences vocales de l'utilisateur"""
        try:
            from ..models import VoicePreference
            
            preference, created = VoicePreference.objects.get_or_create(
                user=request.user
            )
            
            # Mettre à jour les champs fournis
            for field in ['tts_enabled', 'voice_commands_enabled', 'preferred_voice_speed', 
                         'preferred_voice_pitch', 'auto_listen', 'noise_suppression', 
                         'sensitivity', 'conversation_mode', 'pronunciation_feedback']:
                if field in request.data:
                    setattr(preference, field, request.data[field])
            
            preference.save()
            
            return Response({
                'success': True,
                'message': 'Voice preferences updated successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserCommandsView(APIView):
    """
    Gère les commandes personnalisées de l'utilisateur
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Récupère les commandes personnalisées de l'utilisateur"""
        try:
            from ..models import VoiceCommand
            
            commands = VoiceCommand.objects.filter(user=request.user, is_active=True)
            
            commands_data = []
            for cmd in commands:
                commands_data.append({
                    'id': cmd.id,
                    'trigger_phrase': cmd.trigger_phrase,
                    'action_type': cmd.action_type,
                    'action_params': cmd.action_params,
                    'usage_count': cmd.usage_count,
                    'created_at': cmd.created_at.isoformat()
                })
            
            return Response({
                'success': True,
                'commands': commands_data,
                'total': len(commands_data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, command_id=None):
        """Supprime une commande personnalisée"""
        try:
            from ..models import VoiceCommand
            
            if not command_id:
                command_id = request.data.get('command_id')
            
            command = VoiceCommand.objects.get(
                id=command_id, 
                user=request.user
            )
            command.delete()
            
            return Response({
                'success': True,
                'message': 'Command deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except VoiceCommand.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Command not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLanguageView(APIView):
    """
    Récupère la langue native de l'utilisateur pour la reconnaissance vocale
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Récupère la langue native de l'utilisateur"""
        try:
            user = request.user
            native_language = getattr(user, 'native_language', 'fr')
            
            return Response({
                'success': True,
                'native_language': native_language,
                'interface_language': getattr(request, 'LANGUAGE_CODE', 'fr')
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'native_language': 'fr'  # Fallback
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserInfoView(APIView):
    """
    Récupère des informations sur l'utilisateur pour l'assistant vocal
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Récupère des informations spécifiques sur l'utilisateur"""
        try:
            info_type = request.data.get('info_type')
            user = request.user
            
            if info_type == 'native_language':
                return Response({
                    'success': True,
                    'info': user.get_native_language_display() if hasattr(user, 'get_native_language_display') else user.native_language,
                    'raw_value': user.native_language
                })
            
            elif info_type == 'target_language':
                return Response({
                    'success': True,
                    'info': user.get_target_language_display() if hasattr(user, 'get_target_language_display') else user.target_language,
                    'raw_value': user.target_language
                })
            
            elif info_type == 'language_level':
                return Response({
                    'success': True,
                    'info': user.language_level,
                    'raw_value': user.language_level
                })
            
            elif info_type == 'profile_summary':
                return Response({
                    'success': True,
                    'info': {
                        'username': user.username,
                        'native_language': user.get_native_language_display() if hasattr(user, 'get_native_language_display') else user.native_language,
                        'target_language': user.get_target_language_display() if hasattr(user, 'get_target_language_display') else user.target_language,
                        'language_level': user.language_level
                    }
                })
            
            else:
                return Response({
                    'success': False,
                    'error': 'Type d\'information non reconnu'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateUserSettingView(APIView):
    """
    Met à jour les paramètres utilisateur via l'assistant vocal
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Met à jour un paramètre utilisateur spécifique"""
        try:
            setting = request.data.get('setting')
            value = request.data.get('value')
            user = request.user
            
            # Vérifier que le paramètre est autorisé
            allowed_settings = ['native_language', 'target_language', 'language_level']
            
            if setting not in allowed_settings:
                return Response({
                    'success': False,
                    'error': f'Paramètre {setting} non autorisé'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Valider la valeur selon le type de paramètre
            if setting in ['native_language', 'target_language']:
                from apps.authentication.models import LANGUAGE_CHOICES
                valid_values = [choice[0] for choice in LANGUAGE_CHOICES]
                if value not in valid_values:
                    return Response({
                        'success': False,
                        'error': f'Valeur {value} non valide pour {setting}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            elif setting == 'language_level':
                from apps.authentication.models import LEVEL_CHOICES
                valid_values = [choice[0] for choice in LEVEL_CHOICES]
                if value not in valid_values:
                    return Response({
                        'success': False,
                        'error': f'Niveau {value} non valide'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier que native_language != target_language
            if setting == 'native_language' and value == user.target_language:
                return Response({
                    'success': False,
                    'error': 'La langue native ne peut pas être la même que la langue cible'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if setting == 'target_language' and value == user.native_language:
                return Response({
                    'success': False,
                    'error': 'La langue cible ne peut pas être la même que la langue native'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mettre à jour le paramètre
            old_value = getattr(user, setting)
            setattr(user, setting, value)
            user.save()
            
            return Response({
                'success': True,
                'setting': setting,
                'old_value': old_value,
                'new_value': value,
                'message': f'{setting} mis à jour de {old_value} vers {value}'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SystemInfoView(APIView):
    """
    Récupère des informations système sur Linguify
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Récupère des informations système"""
        try:
            info_type = request.data.get('info_type')
            
            if info_type == 'user_count':
                from apps.authentication.models import User
                total_users = User.objects.count()
                active_users = User.objects.filter(is_active=True).count()
                
                return Response({
                    'success': True,
                    'info': {
                        'user_count': total_users,
                        'active_users': active_users
                    }
                })
            
            else:
                return Response({
                    'success': False,
                    'error': 'Type d\'information système non reconnu'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserStatsView(APIView):
    """
    Récupère les statistiques utilisateur pour l'assistant vocal
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Récupère les statistiques utilisateur"""
        try:
            stats_type = request.data.get('stats_type')
            user = request.user
            
            if stats_type == 'learning_progress':
                # Simuler des données de progression (à remplacer par de vraies données)
                return Response({
                    'success': True,
                    'stats': {
                        'lessons_completed': 12,  # À calculer depuis la base de données
                        'progress_percentage': 85,  # À calculer
                        'current_streak': 5
                    }
                })
            
            elif stats_type == 'study_time':
                return Response({
                    'success': True,
                    'stats': {
                        'total_study_minutes': 120,  # À calculer depuis la base de données
                        'this_week_minutes': 45,
                        'today_minutes': 15
                    }
                })
            
            else:
                return Response({
                    'success': False,
                    'error': 'Type de statistiques non reconnu'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIAssistantView(APIView):
    """
    Assistant IA conversationnel pour Linguify
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Traite une demande conversationnelle avec l'IA"""
        try:
            from ..services import voice_service
            
            user_input = request.data.get('message', '').strip()
            context_type = request.data.get('context_type', 'general')
            
            if not user_input:
                return Response({
                    'success': False,
                    'error': 'Message requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Construire le contexte utilisateur
            user_context = {
                'user_id': request.user.id,
                'username': request.user.username,
                'native_language': getattr(request.user, 'native_language', 'FR'),
                'target_language': getattr(request.user, 'target_language', 'EN'),
                'language_level': getattr(request.user, 'language_level', 'A1'),
                'context_type': context_type
            }
            
            # Traiter avec l'IA
            ai_result = voice_service.ai_service.process_natural_language_command(
                user_input, 
                user_context
            )
            
            return Response({
                'success': True,
                'ai_response': ai_result,
                'processed_at': time.time()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIRecommendationView(APIView):
    """
    Recommandations personnalisées par IA
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Génère des recommandations IA personnalisées"""
        try:
            recommendation_type = request.data.get('type', 'learning')
            user = request.user
            
            # Simuler des recommandations intelligentes
            recommendations = self._generate_recommendations(user, recommendation_type)
            
            return Response({
                'success': True,
                'recommendations': recommendations,
                'user_level': user.language_level,
                'personalized': True
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_recommendations(self, user, rec_type):
        """Génère des recommandations basées sur le profil utilisateur"""
        
        base_recommendations = {
            'learning': [
                {
                    'title': 'Session de vocabulaire',
                    'description': f'Apprendre 10 nouveaux mots en {user.target_language}',
                    'action': 'navigate',
                    'url': '/learning/?focus=vocabulary',
                    'duration': '15 minutes',
                    'difficulty': user.language_level
                },
                {
                    'title': 'Quiz interactif',
                    'description': 'Tester vos connaissances récentes',
                    'action': 'navigate', 
                    'url': '/quizz/',
                    'duration': '10 minutes',
                    'difficulty': user.language_level
                }
            ],
            'practice': [
                {
                    'title': 'Conversation IA',
                    'description': 'Pratiquer une conversation guidée',
                    'action': 'navigate',
                    'url': '/language_ai/',
                    'duration': '20 minutes',
                    'skill': 'speaking'
                }
            ]
        }
        
        return base_recommendations.get(rec_type, base_recommendations['learning'])


class FlashcardCreationView(APIView):
    """
    Création de flashcards via l'assistant vocal IA
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Crée une flashcard via commande vocale IA"""
        try:
            from apps.revision.models.revision_flashcard import FlashcardDeck, Flashcard
            
            # Paramètres de la flashcard depuis l'IA
            front_text = request.data.get('front_text', '').strip()
            back_text = request.data.get('back_text', '').strip()
            deck_name = request.data.get('deck_cible', 'Vocabulaire IA')
            front_language = request.data.get('front_language', 'fr')
            back_language = request.data.get('back_language', 'en')
            
            if not front_text or not back_text:
                return Response({
                    'success': False,
                    'error': 'Texte recto et verso requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Créer ou récupérer le deck
            deck, created = FlashcardDeck.objects.get_or_create(
                user=request.user,
                name=deck_name,
                defaults={
                    'description': f'Deck créé automatiquement par l\'IA vocale',
                    'is_active': True
                }
            )
            
            # Vérifier si la flashcard existe déjà
            existing_card = Flashcard.objects.filter(
                user=request.user,
                deck=deck,
                front_text=front_text,
                back_text=back_text
            ).first()
            
            if existing_card:
                return Response({
                    'success': True,
                    'message': f'La flashcard "{front_text}" existe déjà dans le deck "{deck_name}"',
                    'flashcard_id': existing_card.id,
                    'deck_id': deck.id,
                    'action': 'existing'
                })
            
            # Créer la nouvelle flashcard
            flashcard = Flashcard.objects.create(
                user=request.user,
                deck=deck,
                front_text=front_text,
                back_text=back_text,
                front_language=front_language,
                back_language=back_language
            )
            
            return Response({
                'success': True,
                'message': f'Flashcard "{front_text}" → "{back_text}" créée avec succès dans "{deck_name}"',
                'flashcard_id': flashcard.id,
                'deck_id': deck.id,
                'deck_created': created,
                'action': 'created'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VocabularyExtractionView(APIView):
    """
    Extraction intelligente de vocabulaire pour créer des flashcards
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Extrait du vocabulaire d'un texte et crée des flashcards"""
        try:
            from apps.revision.models.revision_flashcard import FlashcardDeck, Flashcard
            from ..claude_service import claude_service
            
            text_content = request.data.get('text', '').strip()
            deck_name = request.data.get('deck_name', 'Vocabulaire extrait')
            target_language = request.data.get('target_language', 'en')
            
            if not text_content:
                return Response({
                    'success': False,
                    'error': 'Texte à analyser requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Utiliser Claude pour extraire le vocabulaire important
            extraction_prompt = f"""
            Extrait les 5-10 mots les plus importants de ce texte pour créer des flashcards de vocabulaire:
            
            "{text_content}"
            
            Langue cible: {target_language}
            
            Retourne uniquement un JSON avec cette structure:
            {{
                "mots_extraits": [
                    {{"front": "mot_original", "back": "traduction", "importance": 0.9}},
                    ...
                ]
            }}
            """
            
            # Pour l'instant, simulation de l'extraction
            extracted_words = [
                {"front": "important", "back": "important", "importance": 0.9},
                {"front": "apprendre", "back": "learn", "importance": 0.8},
                {"front": "vocabulaire", "back": "vocabulary", "importance": 0.85}
            ]
            
            # Créer ou récupérer le deck
            deck, created = FlashcardDeck.objects.get_or_create(
                user=request.user,
                name=deck_name,
                defaults={
                    'description': f'Vocabulaire extrait automatiquement par l\'IA',
                    'is_active': True
                }
            )
            
            created_cards = []
            existing_cards = []
            
            for word_data in extracted_words:
                front_text = word_data['front']
                back_text = word_data['back']
                
                # Vérifier si la carte existe déjà
                existing = Flashcard.objects.filter(
                    user=request.user,
                    deck=deck,
                    front_text=front_text
                ).first()
                
                if existing:
                    existing_cards.append(front_text)
                else:
                    flashcard = Flashcard.objects.create(
                        user=request.user,
                        deck=deck,
                        front_text=front_text,
                        back_text=back_text,
                        front_language='fr',
                        back_language=target_language
                    )
                    created_cards.append(front_text)
            
            return Response({
                'success': True,
                'deck_name': deck_name,
                'deck_id': deck.id,
                'created_cards': created_cards,
                'existing_cards': existing_cards,
                'total_created': len(created_cards),
                'message': f'{len(created_cards)} nouvelles flashcards créées dans "{deck_name}"'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
