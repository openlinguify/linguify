import json
import logging
from datetime import datetime
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .models.chat_models import Call, CallParticipant
from apps.authentication.models import User

logger = logging.getLogger(__name__)

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'call_{self.room_id}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.add_participant_to_call()
        
        await self.notify_user_joined()
    
    async def disconnect(self, close_code):
        await self.remove_participant_from_call()
        
        await self.notify_user_left()
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'offer':
                await self.handle_offer(data)
            elif message_type == 'answer':
                await self.handle_answer(data)
            elif message_type == 'ice-candidate':
                await self.handle_ice_candidate(data)
            elif message_type == 'mute-audio':
                await self.handle_mute_audio(data)
            elif message_type == 'mute-video':
                await self.handle_mute_video(data)
            elif message_type == 'end-call':
                await self.handle_end_call(data)
            elif message_type == 'call-status':
                await self.handle_call_status(data)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
    
    async def handle_offer(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_offer',
                'offer': data['offer'],
                'sender_id': str(self.user.id),
                'sender_name': self.user.username,
            }
        )
    
    async def handle_answer(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_answer',
                'answer': data['answer'],
                'sender_id': str(self.user.id),
                'sender_name': self.user.username,
            }
        )
    
    async def handle_ice_candidate(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'webrtc_ice_candidate',
                'candidate': data['candidate'],
                'sender_id': str(self.user.id),
            }
        )
    
    async def handle_mute_audio(self, data):
        is_muted = data.get('is_muted', False)
        
        await self.update_participant_mute_status(audio_muted=is_muted)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_mute_audio',
                'user_id': str(self.user.id),
                'is_muted': is_muted,
            }
        )
    
    async def handle_mute_video(self, data):
        is_muted = data.get('is_muted', False)
        
        await self.update_participant_mute_status(video_muted=is_muted)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_mute_video',
                'user_id': str(self.user.id),
                'is_muted': is_muted,
            }
        )
    
    async def handle_call_status(self, data):
        status = data.get('status')
        if status in ['answered', 'declined', 'ended']:
            await self.update_call_status(status)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_status_update',
                    'status': status,
                    'user_id': str(self.user.id),
                }
            )
    
    async def handle_end_call(self, data):
        await self.update_call_status('ended')
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'call_ended',
                'user_id': str(self.user.id),
            }
        )
    
    async def webrtc_offer(self, event):
        if str(self.user.id) != event['sender_id']:
            await self.send(text_data=json.dumps({
                'type': 'offer',
                'offer': event['offer'],
                'sender_id': event['sender_id'],
                'sender_name': event['sender_name'],
            }))
    
    async def webrtc_answer(self, event):
        if str(self.user.id) != event['sender_id']:
            await self.send(text_data=json.dumps({
                'type': 'answer',
                'answer': event['answer'],
                'sender_id': event['sender_id'],
                'sender_name': event['sender_name'],
            }))
    
    async def webrtc_ice_candidate(self, event):
        if str(self.user.id) != event['sender_id']:
            await self.send(text_data=json.dumps({
                'type': 'ice-candidate',
                'candidate': event['candidate'],
                'sender_id': event['sender_id'],
            }))
    
    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user-joined',
            'user_id': event['user_id'],
            'username': event['username'],
        }))
    
    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user-left',
            'user_id': event['user_id'],
            'username': event['username'],
        }))
    
    async def user_mute_audio(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user-mute-audio',
            'user_id': event['user_id'],
            'is_muted': event['is_muted'],
        }))
    
    async def user_mute_video(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user-mute-video',
            'user_id': event['user_id'],
            'is_muted': event['is_muted'],
        }))
    
    async def call_ended(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call-ended',
            'user_id': event['user_id'],
        }))
    
    async def call_status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call-status-update',
            'status': event['status'],
            'user_id': event['user_id'],
        }))
    
    async def notify_user_joined(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': str(self.user.id),
                'username': self.user.username,
            }
        )
    
    async def notify_user_left(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': str(self.user.id),
                'username': self.user.username,
            }
        )
    
    @sync_to_async
    def add_participant_to_call(self):
        try:
            call = Call.objects.get(room_id=self.room_id)
            CallParticipant.objects.get_or_create(
                call=call,
                user=self.user,
                defaults={'joined_at': timezone.now()}
            )
        except Call.DoesNotExist:
            logger.error(f"Call with room_id {self.room_id} does not exist")
    
    @sync_to_async
    def remove_participant_from_call(self):
        try:
            call = Call.objects.get(room_id=self.room_id)
            participant = CallParticipant.objects.filter(
                call=call,
                user=self.user,
                left_at__isnull=True
            ).first()
            
            if participant:
                participant.left_at = timezone.now()
                participant.save()
                
                active_participants = CallParticipant.objects.filter(
                    call=call,
                    left_at__isnull=True
                ).count()
                
                if active_participants == 0:
                    call.status = 'ended'
                    call.ended_at = timezone.now()
                    if call.started_at:
                        duration = (call.ended_at - call.started_at).total_seconds()
                        call.duration = int(duration)
                    call.save()
        except Call.DoesNotExist:
            logger.error(f"Call with room_id {self.room_id} does not exist")
    
    @sync_to_async
    def update_participant_mute_status(self, audio_muted=None, video_muted=None):
        try:
            call = Call.objects.get(room_id=self.room_id)
            participant = CallParticipant.objects.filter(
                call=call,
                user=self.user,
                left_at__isnull=True
            ).first()
            
            if participant:
                if audio_muted is not None:
                    participant.is_muted_audio = audio_muted
                if video_muted is not None:
                    participant.is_muted_video = video_muted
                participant.save()
        except Call.DoesNotExist:
            logger.error(f"Call with room_id {self.room_id} does not exist")
    
    @sync_to_async
    def update_call_status(self, status):
        try:
            call = Call.objects.get(room_id=self.room_id)
            call.status = status
            if status == 'ended':
                call.ended_at = timezone.now()
                if call.started_at:
                    duration = (call.ended_at - call.started_at).total_seconds()
                    call.duration = int(duration)
            call.save()
        except Call.DoesNotExist:
            logger.error(f"Call with room_id {self.room_id} does not exist")