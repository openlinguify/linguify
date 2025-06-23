from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.utils.decorators import method_decorator
from django.views.generic import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json

from apps.authentication.models import User
from .models import Profile, Conversation, ChatMessage, FriendRequest
from .serializers import ConversationSerializer, ChatMessageSerializer


@login_required
@require_http_methods(["POST"])
def start_conversation(request):
    """Start a new conversation with another user"""
    try:
        data = json.loads(request.body)
        other_user_id = data.get('user_id')
        
        if not other_user_id:
            return JsonResponse({'error': 'User ID is required'}, status=400)
        
        other_user = get_object_or_404(User, id=other_user_id)
        
        # Get or create profiles
        user_profile, _ = Profile.objects.get_or_create(user=request.user)
        other_profile, _ = Profile.objects.get_or_create(user=other_user)
        
        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            participants=user_profile
        ).filter(
            participants=other_profile
        ).first()
        
        if existing_conversation:
            return JsonResponse({
                'success': True,
                'conversation_id': existing_conversation.id,
                'message': 'Conversation already exists'
            })
        
        # Create new conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(user_profile, other_profile)
        
        return JsonResponse({
            'success': True,
            'conversation_id': conversation.id,
            'message': 'Conversation created successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_conversations(request):
    """Get all conversations for the current user"""
    try:
        user_profile, _ = Profile.objects.get_or_create(user=request.user)
        
        conversations = Conversation.objects.filter(
            participants=user_profile
        ).prefetch_related('participants__user', 'messages').annotate(
            unread_count=Count('messages', filter=Q(messages__receiver=user_profile, messages__is_read=False))
        ).order_by('-last_message')
        
        conversations_data = []
        for conversation in conversations:
            other_participant = conversation.participants.exclude(id=user_profile.id).first()
            if other_participant:
                last_message = conversation.messages.order_by('-timestamp').first()
                
                conversations_data.append({
                    'id': conversation.id,
                    'participant': {
                        'id': other_participant.user.id,
                        'username': other_participant.user.username,
                        'name': other_participant.user.name or other_participant.user.username,
                        'avatar': other_participant.user.get_profile_picture_url() if hasattr(other_participant.user, 'get_profile_picture_url') else None,
                        'is_online': other_participant.is_online,
                        'native_language': other_participant.user.get_native_language_display() if hasattr(other_participant.user, 'get_native_language_display') else None,
                        'target_language': other_participant.user.get_target_language_display() if hasattr(other_participant.user, 'get_target_language_display') else None,
                    },
                    'last_message': {
                        'content': last_message.message if last_message else None,
                        'timestamp': last_message.timestamp.isoformat() if last_message else None,
                        'sender': last_message.sender.user.username if last_message else None
                    } if last_message else None,
                    'unread_count': conversation.unread_count,
                    'last_activity': conversation.last_message.isoformat()
                })
        
        return JsonResponse({
            'success': True,
            'conversations': conversations_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_conversation_messages(request, conversation_id):
    """Get messages for a specific conversation"""
    try:
        user_profile, _ = Profile.objects.get_or_create(user=request.user)
        
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Check if user is participant
        if not conversation.participants.filter(id=user_profile.id).exists():
            return JsonResponse({'error': 'You are not a participant in this conversation'}, status=403)
        
        # Get messages
        messages = conversation.messages.select_related('sender__user').order_by('timestamp')
        
        # Mark messages as read
        unread_messages = messages.filter(receiver=user_profile, is_read=False)
        unread_messages.update(is_read=True)
        
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': message.id,
                'content': message.message,
                'sender': {
                    'id': message.sender.user.id,
                    'username': message.sender.user.username,
                    'name': message.sender.user.name or message.sender.user.username,
                    'avatar': message.sender.user.get_profile_picture_url() if hasattr(message.sender.user, 'get_profile_picture_url') else None
                },
                'timestamp': message.timestamp.isoformat(),
                'is_own_message': message.sender.user.id == request.user.id
            })
        
        return JsonResponse({
            'success': True,
            'messages': messages_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def send_message(request, conversation_id):
    """Send a message in a conversation"""
    try:
        data = json.loads(request.body)
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return JsonResponse({'error': 'Message content is required'}, status=400)
        
        user_profile, _ = Profile.objects.get_or_create(user=request.user)
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Check if user is participant
        if not conversation.participants.filter(id=user_profile.id).exists():
            return JsonResponse({'error': 'You are not a participant in this conversation'}, status=403)
        
        # Get receiver
        receiver_profile = conversation.participants.exclude(id=user_profile.id).first()
        if not receiver_profile:
            return JsonResponse({'error': 'No other participant found'}, status=400)
        
        # Create message
        message = ChatMessage.objects.create(
            conversation=conversation,
            sender=user_profile,
            receiver=receiver_profile,
            message=message_content
        )
        
        # Update conversation last message time
        conversation.save()
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.message,
                'sender': {
                    'id': user_profile.user.id,
                    'username': user_profile.user.username,
                    'name': user_profile.user.name or user_profile.user.username,
                    'avatar': user_profile.user.get_profile_picture_url() if hasattr(user_profile.user, 'get_profile_picture_url') else None
                },
                'timestamp': message.timestamp.isoformat(),
                'is_own_message': True
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_language_partners(request):
    """Get potential language partners based on language exchange"""
    try:
        user_profile, _ = Profile.objects.get_or_create(user=request.user)
        user = request.user
        
        # Get users whose native language is the current user's target language
        # and whose target language is the current user's native language
        potential_partners = User.objects.filter(
            Q(native_language=user.target_language, target_language=user.native_language) |
            Q(native_language=user.target_language) |
            Q(target_language=user.native_language)
        ).exclude(
            id=user.id
        ).exclude(
            id__in=user_profile.friends.values_list('user_id', flat=True)
        ).select_related('profile')
        
        partners_data = []
        for partner in potential_partners:
            partner_profile, _ = Profile.objects.get_or_create(user=partner)
            
            # Calculate compatibility score
            compatibility_score = 0
            if partner.native_language == user.target_language:
                compatibility_score += 50
            if partner.target_language == user.native_language:
                compatibility_score += 50
            
            # Check if there's mutual language learning opportunity
            is_mutual_exchange = (
                partner.native_language == user.target_language and
                partner.target_language == user.native_language
            )
            
            partners_data.append({
                'id': partner.id,
                'username': partner.username,
                'name': partner.name or partner.username,
                'avatar': partner.get_profile_picture_url() if hasattr(partner, 'get_profile_picture_url') else None,
                'native_language': partner.get_native_language_display() if hasattr(partner, 'get_native_language_display') else None,
                'target_language': partner.get_target_language_display() if hasattr(partner, 'get_target_language_display') else None,
                'bio': partner_profile.bio,
                'teaching_languages': partner_profile.teaching_languages,
                'learning_languages': partner_profile.learning_languages,
                'is_online': partner_profile.is_online,
                'compatibility_score': compatibility_score,
                'is_mutual_exchange': is_mutual_exchange,
                'exchange_type': 'mutual' if is_mutual_exchange else 'one-way'
            })
        
        # Sort by compatibility score
        partners_data.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'partners': partners_data[:20]  # Limit to top 20
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def create_language_exchange_room(request):
    """Create a temporary language exchange room"""
    try:
        data = json.loads(request.body)
        room_name = data.get('room_name', '').strip()
        language_focus = data.get('language_focus', '')
        
        if not room_name:
            return JsonResponse({'error': 'Room name is required'}, status=400)
        
        # For now, just return success - in a real implementation, 
        # you might want to store room info in database
        return JsonResponse({
            'success': True,
            'room_id': room_name,
            'websocket_url': f'/ws/community/language-exchange/{room_name}/',
            'message': 'Language exchange room created successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_friend_suggestions(request):
    """Get friend suggestions based on language learning compatibility"""
    try:
        user_profile, _ = Profile.objects.get_or_create(user=request.user)
        user = request.user
        
        # Get users learning similar languages or native speakers of target language
        suggestions = User.objects.filter(
            Q(target_language=user.target_language) |  # Same target language
            Q(native_language=user.target_language) |  # Native speakers of user's target
            Q(target_language=user.native_language)    # Learning user's native language
        ).exclude(
            id=user.id
        ).exclude(
            id__in=user_profile.friends.values_list('user_id', flat=True)
        ).select_related('profile')
        
        suggestions_data = []
        for suggested_user in suggestions:
            suggested_profile, _ = Profile.objects.get_or_create(user=suggested_user)
            
            # Calculate suggestion reason
            reasons = []
            if suggested_user.native_language == user.target_language:
                reasons.append(f"Native {suggested_user.get_native_language_display()} speaker")
            if suggested_user.target_language == user.target_language:
                reasons.append(f"Also learning {suggested_user.get_target_language_display()}")
            if suggested_user.target_language == user.native_language:
                reasons.append(f"Learning {user.get_native_language_display()}")
            
            suggestions_data.append({
                'id': suggested_user.id,
                'username': suggested_user.username,
                'name': suggested_user.name or suggested_user.username,
                'avatar': suggested_user.get_profile_picture_url() if hasattr(suggested_user, 'get_profile_picture_url') else None,
                'native_language': suggested_user.get_native_language_display() if hasattr(suggested_user, 'get_native_language_display') else None,
                'target_language': suggested_user.get_target_language_display() if hasattr(suggested_user, 'get_target_language_display') else None,
                'bio': suggested_profile.bio,
                'is_online': suggested_profile.is_online,
                'suggestion_reasons': reasons[:2]  # Limit to 2 main reasons
            })
        
        return JsonResponse({
            'success': True,
            'suggestions': suggestions_data[:10]  # Limit to top 10
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)