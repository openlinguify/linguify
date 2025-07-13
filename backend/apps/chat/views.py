from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
from apps.community.models import Conversation, ChatMessage, Profile
import json

User = get_user_model()

@login_required
def chat_redirect(request):
    """Page de chat dédiée"""
    # Page de test pour le debug
    if request.GET.get('test') == '1':
        return render(request, 'chat/test.html')
    
    # Si l'utilisateur demande explicitement des infos, afficher la page info
    if request.GET.get('info') == '1':
        return render(request, 'chat/info.html')
    
    # Page de chat dédiée par défaut
    return render(request, 'chat/chat_page.html')

@login_required
@require_http_methods(["GET"])
def get_conversations(request):
    """Récupère les conversations de l'utilisateur depuis community"""
    try:
        # Obtenir le profil community de l'utilisateur
        profile = Profile.objects.get(user=request.user)
        
        # Récupérer les conversations
        conversations = Conversation.objects.filter(participants=profile).order_by('-last_message')
        
        conversations_data = []
        for conv in conversations:
            # Obtenir l'autre participant
            other_participant = conv.participants.exclude(id=profile.id).first()
            
            # Dernier message
            last_message = ChatMessage.objects.filter(conversation=conv).order_by('-timestamp').first()
            
            # Messages non lus
            unread_count = ChatMessage.objects.filter(
                conversation=conv,
                receiver=profile,
                is_read=False
            ).count()
            
            conversations_data.append({
                'id': conv.id,
                'participant': {
                    'id': other_participant.user.id if other_participant else None,
                    'username': other_participant.user.username if other_participant else 'Inconnu',
                    'is_online': other_participant.is_online if other_participant else False,
                } if other_participant else None,
                'last_message': {
                    'content': last_message.message if last_message else '',
                    'timestamp': last_message.timestamp.isoformat() if last_message else None,
                    'sender': last_message.sender.user.username if last_message else None,
                } if last_message else None,
                'unread_count': unread_count,
            })
        
        return JsonResponse({
            'status': 'success',
            'conversations': conversations_data
        })
        
    except Profile.DoesNotExist:
        # Créer un profil community si il n'existe pas
        Profile.objects.create(user=request.user)
        return JsonResponse({
            'status': 'success',
            'conversations': []
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_messages(request, conversation_id):
    """Récupère les messages d'une conversation"""
    try:
        profile = Profile.objects.get(user=request.user)
        conversation = Conversation.objects.get(id=conversation_id, participants=profile)
        
        # Récupérer les messages
        messages = ChatMessage.objects.filter(conversation=conversation).order_by('timestamp')
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'content': msg.message,
                'timestamp': msg.timestamp.isoformat(),
                'sender': {
                    'id': msg.sender.user.id,
                    'username': msg.sender.user.username,
                },
                'is_own_message': msg.sender == profile,
                'is_read': msg.is_read,
            })
        
        # Marquer les messages comme lus
        ChatMessage.objects.filter(
            conversation=conversation,
            receiver=profile,
            is_read=False
        ).update(is_read=True)
        
        return JsonResponse({
            'status': 'success',
            'messages': messages_data
        })
        
    except (Profile.DoesNotExist, Conversation.DoesNotExist):
        return JsonResponse({
            'status': 'error',
            'message': 'Conversation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def start_conversation(request):
    """Démarre une nouvelle conversation avec un utilisateur"""
    try:
        data = json.loads(request.body)
        target_user_id = data.get('user_id')
        
        if not target_user_id:
            return JsonResponse({
                'status': 'error',
                'message': 'user_id required'
            }, status=400)
        
        # Vérifier que l'utilisateur cible existe
        target_user = User.objects.get(id=target_user_id)
        target_profile = Profile.objects.get(user=target_user)
        current_profile = Profile.objects.get(user=request.user)
        
        # Vérifier si une conversation existe déjà
        existing_conversation = Conversation.objects.filter(
            participants=current_profile
        ).filter(
            participants=target_profile
        ).first()
        
        if existing_conversation:
            return JsonResponse({
                'status': 'success',
                'conversation_id': existing_conversation.id,
                'message': 'Conversation already exists'
            })
        
        # Créer une nouvelle conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(current_profile, target_profile)
        
        return JsonResponse({
            'status': 'success',
            'conversation_id': conversation.id,
            'message': 'Conversation created'
        })
        
    except (User.DoesNotExist, Profile.DoesNotExist):
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def search_users(request):
    """Recherche d'utilisateurs pour démarrer une conversation"""
    try:
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({
                'status': 'error',
                'message': 'Query too short'
            }, status=400)
        
        # Rechercher des utilisateurs
        users = User.objects.filter(
            username__icontains=query
        ).exclude(id=request.user.id)[:10]
        
        users_data = []
        for user in users:
            try:
                profile = Profile.objects.get(user=user)
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'is_online': profile.is_online,
                })
            except Profile.DoesNotExist:
                # Créer le profil si nécessaire
                Profile.objects.create(user=user)
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'is_online': False,
                })
        
        return JsonResponse({
            'status': 'success',
            'users': users_data
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Envoie un message dans une conversation"""
    try:
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        message_content = data.get('message', '').strip()
        
        if not conversation_id or not message_content:
            return JsonResponse({
                'status': 'error',
                'message': 'conversation_id and message required'
            }, status=400)
        
        # Vérifier que l'utilisateur a accès à cette conversation
        current_profile = Profile.objects.get(user=request.user)
        conversation = Conversation.objects.get(id=conversation_id, participants=current_profile)
        
        # Trouver le destinataire (l'autre participant)
        receiver = conversation.participants.exclude(id=current_profile.id).first()
        if not receiver:
            return JsonResponse({
                'status': 'error',
                'message': 'No receiver found in conversation'
            }, status=400)
        
        # Créer le message avec le destinataire
        message = ChatMessage.objects.create(
            conversation=conversation,
            sender=current_profile,
            receiver=receiver,
            message=message_content
        )
        
        # Mettre à jour la conversation
        conversation.last_message = message.timestamp
        conversation.save()
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'content': message.message,
                'timestamp': message.timestamp.isoformat(),
                'sender': {
                    'id': message.sender.user.id,
                    'username': message.sender.user.username,
                },
                'is_own_message': True,
            }
        })
        
    except (Profile.DoesNotExist, Conversation.DoesNotExist):
        return JsonResponse({
            'status': 'error',
            'message': 'Conversation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
