# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from apps.authentication.models import User
from .models import Profile, ChatMessage, Conversation
import json
import logging

logger = logging.getLogger(__name__)


class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            await self.update_user_online_status(True)
            await self.channel_layer.group_add(f'user_status_{self.user.id}', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.update_user_online_status(False)
            await self.channel_layer.group_discard(f'user_status_{self.user.id}', self.channel_name)

    @database_sync_to_async
    def update_user_online_status(self, is_online):
        try:
            profile, created = Profile.objects.get_or_create(user=self.user)
            profile.is_online = is_online
            profile.save()
        except Exception as e:
            logger.error(f"Error updating user status: {e}")


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            await self.channel_layer.group_add(f'notifications_{self.user.id}', self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(f'notifications_{self.user.id}', self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event['notification']))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'

        if self.user.is_authenticated:
            # Check if user is participant in this conversation
            is_participant = await self.check_conversation_participant()
            if is_participant:
                await self.channel_layer.group_add(
                    self.conversation_group_name,
                    self.channel_name
                )
                await self.accept()
            else:
                await self.close()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'conversation_group_name'):
            await self.channel_layer.group_discard(
                self.conversation_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')
            
            if message_type == 'message':
                message = text_data_json['message']
                
                # Save message to database
                saved_message = await self.save_message(message)
                
                if saved_message:
                    # Send message to conversation group
                    await self.channel_layer.group_send(
                        self.conversation_group_name,
                        {
                            'type': 'chat_message',
                            'message': {
                                'id': saved_message['id'],
                                'content': saved_message['content'],
                                'sender': saved_message['sender'],
                                'timestamp': saved_message['timestamp'],
                                'is_translation': saved_message.get('is_translation', False)
                            }
                        }
                    )
            elif message_type == 'typing':
                # Handle typing indicators
                await self.channel_layer.group_send(
                    self.conversation_group_name,
                    {
                        'type': 'typing_indicator',
                        'user': self.user.username,
                        'is_typing': text_data_json.get('is_typing', False)
                    }
                )
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received in ChatConsumer")
        except Exception as e:
            logger.error(f"Error in ChatConsumer receive: {e}")

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message
        }))

    async def typing_indicator(self, event):
        # Don't send typing indicator back to the person who's typing
        if event['user'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user': event['user'],
                'is_typing': event['is_typing']
            }))

    @database_sync_to_async
    def check_conversation_participant(self):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            user_profile = Profile.objects.get(user=self.user)
            return conversation.participants.filter(id=user_profile.id).exists()
        except (Conversation.DoesNotExist, Profile.DoesNotExist):
            return False

    @database_sync_to_async
    def save_message(self, message_content):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            sender_profile = Profile.objects.get(user=self.user)
            
            # Get the other participant (receiver)
            receiver_profile = conversation.participants.exclude(id=sender_profile.id).first()
            
            if receiver_profile:
                message = ChatMessage.objects.create(
                    conversation=conversation,
                    sender=sender_profile,
                    receiver=receiver_profile,
                    message=message_content
                )
                
                # Update conversation last message time
                conversation.save()  # This will update last_message field
                
                return {
                    'id': message.id,
                    'content': message.message,
                    'sender': {
                        'id': sender_profile.user.id,
                        'username': sender_profile.user.username,
                        'name': sender_profile.user.name or sender_profile.user.username,
                        'avatar': sender_profile.user.get_profile_picture_url() if hasattr(sender_profile.user, 'get_profile_picture_url') else None
                    },
                    'timestamp': message.timestamp.isoformat()
                }
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return None


class LanguageExchangeConsumer(AsyncWebsocketConsumer):
    """Special consumer for language exchange features"""
    
    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'language_exchange_{self.room_name}'

        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            
            # Notify others that user joined
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'user': self.user.username,
                    'native_language': getattr(self.user, 'native_language', 'Unknown'),
                    'target_language': getattr(self.user, 'target_language', 'Unknown')
                }
            )
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Notify others that user left
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user': self.user.username
                }
            )
            
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')
            
            if message_type == 'correction':
                # Handle language corrections
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'language_correction',
                        'original_text': text_data_json['original_text'],
                        'corrected_text': text_data_json['corrected_text'],
                        'explanation': text_data_json.get('explanation', ''),
                        'corrector': self.user.username
                    }
                )
            elif message_type == 'translation_request':
                # Handle translation requests
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'translation_request',
                        'text': text_data_json['text'],
                        'from_language': text_data_json['from_language'],
                        'to_language': text_data_json['to_language'],
                        'requester': self.user.username
                    }
                )
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received in LanguageExchangeConsumer")
        except Exception as e:
            logger.error(f"Error in LanguageExchangeConsumer receive: {e}")

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user': event['user'],
            'native_language': event['native_language'],
            'target_language': event['target_language']
        }))

    async def user_left(self, event):
        if event['user'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user': event['user']
            }))

    async def language_correction(self, event):
        await self.send(text_data=json.dumps({
            'type': 'correction',
            'original_text': event['original_text'],
            'corrected_text': event['corrected_text'],
            'explanation': event['explanation'],
            'corrector': event['corrector']
        }))

    async def translation_request(self, event):
        if event['requester'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'translation_request',
                'text': event['text'],
                'from_language': event['from_language'],
                'to_language': event['to_language'],
                'requester': event['requester']
            }))
