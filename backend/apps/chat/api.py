from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
from django.utils import timezone
import uuid

from .models.chat_models import Call, CallParticipant
from .serializers import ConversationListSerializer, ConversationDetailSerializer, ConversationMessageSerializer
from apps.authentication.models import User
from apps.community.models import Conversation, Profile


@api_view(['GET'])
def conversations_list(request):
    serializer = ConversationListSerializer(request.user.conversations.all(), many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def conversations_detail(request, pk):
    conversation = request.user.conversations.get(pk=pk)
    conversation_serializer = ConversationDetailSerializer(conversation, many=False)
    messages_serializer = ConversationMessageSerializer(conversation.messages.all(), many=True)

    return JsonResponse({
        'conversation': conversation_serializer.data,
        'messages': messages_serializer.data
    }, safe=False)

@api_view(['GET'])
def conversations_start(request, user_id):
    conversations = Conversation.objects.filter(users__in=[user_id]).filter(users__in=[request.user.id])

    if conversations.count() > 0:
        conversation = conversations.first()
        
        return JsonResponse({'success': True, 'conversation_id': conversation.id})
    else:
        user = User.objects.get(pk=user_id)
        conversation = Conversation.objects.create()
        conversation.users.add(request.user)
        conversation.users.add(user)

        return JsonResponse({'success': True, 'conversation_id': conversation.id})

@api_view(['POST'])
def initiate_call(request):
    conversation_id = request.data.get('conversation_id')
    receiver_id = request.data.get('receiver_id')
    call_type = request.data.get('call_type', 'audio')
    
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        receiver = User.objects.get(id=receiver_id)
        
        # Obtenir les profils
        current_profile = Profile.objects.get(user=request.user)
        receiver_profile = Profile.objects.get(user=receiver)
        
        if current_profile not in conversation.participants.all() or receiver_profile not in conversation.participants.all():
            return JsonResponse({
                'success': False,
                'error': 'Invalid conversation or users'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        room_id = str(uuid.uuid4())
        
        call = Call.objects.create(
            conversation=conversation,
            caller=request.user,
            receiver=receiver,
            call_type=call_type,
            room_id=room_id,
            status='initiated'
        )
        
        return JsonResponse({
            'success': True,
            'call_id': str(call.id),
            'room_id': room_id,
            'call_type': call_type
        })
        
    except (Conversation.DoesNotExist, User.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Conversation or user not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def answer_call(request, call_id):
    try:
        call = Call.objects.get(id=call_id)
        
        if request.user != call.receiver:
            return JsonResponse({
                'success': False,
                'error': 'Only the receiver can answer the call'
            }, status=status.HTTP_403_FORBIDDEN)
        
        call.status = 'answered'
        call.save()
        
        return JsonResponse({
            'success': True,
            'room_id': call.room_id
        })
        
    except Call.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Call not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def decline_call(request, call_id):
    try:
        call = Call.objects.get(id=call_id)
        
        if request.user != call.receiver:
            return JsonResponse({
                'success': False,
                'error': 'Only the receiver can decline the call'
            }, status=status.HTTP_403_FORBIDDEN)
        
        call.status = 'declined'
        call.save()
        
        return JsonResponse({'success': True})
        
    except Call.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Call not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def end_call(request, call_id):
    try:
        call = Call.objects.get(id=call_id)
        
        if request.user not in [call.caller, call.receiver]:
            return JsonResponse({
                'success': False,
                'error': 'Only participants can end the call'
            }, status=status.HTTP_403_FORBIDDEN)
        
        call.status = 'ended'
        call.ended_at = timezone.now()
        if call.started_at:
            duration = (call.ended_at - call.started_at).total_seconds()
            call.duration = int(duration)
        call.save()
        
        return JsonResponse({
            'success': True,
            'duration': call.duration
        })
        
    except Call.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Call not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def call_history(request):
    calls_made = Call.objects.filter(caller=request.user).order_by('-started_at')
    calls_received = Call.objects.filter(receiver=request.user).order_by('-started_at')
    
    all_calls = calls_made.union(calls_received).order_by('-started_at')[:50]
    
    call_data = []
    for call in all_calls:
        call_data.append({
            'id': str(call.id),
            'type': call.call_type,
            'status': call.status,
            'caller': {
                'id': str(call.caller.id),
                'username': call.caller.username
            },
            'receiver': {
                'id': str(call.receiver.id),
                'username': call.receiver.username
            },
            'started_at': call.started_at.isoformat() if call.started_at else None,
            'ended_at': call.ended_at.isoformat() if call.ended_at else None,
            'duration': call.duration
        })
    
    return JsonResponse({
        'success': True,
        'calls': call_data
    })