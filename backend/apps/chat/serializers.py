# backend/chat/serializers.py
from rest_framework import serializers
from .models import Conversation, ConversationMessage, Call, CallParticipant
from apps.authentication.serializers import UserSerializer

class ConversationListSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Conversation
        fields = ('id', 'users', 'updated_at')


class ConversationDetailSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Conversation
        fields = ('id', 'users', 'updated_at')

class ConversationMessageSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    sent_to = UserSerializer(read_only=True)
    class Meta:
        model = ConversationMessage
        fields = ('id', 'body', 'sent_to', 'created_by', 'created_at')

class CallParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = CallParticipant
        fields = ('id', 'user', 'joined_at', 'left_at', 'is_muted_audio', 'is_muted_video')

class CallSerializer(serializers.ModelSerializer):
    caller = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    participants = CallParticipantSerializer(many=True, read_only=True)
    conversation = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Call
        fields = (
            'id', 'conversation', 'caller', 'receiver', 'call_type', 
            'status', 'started_at', 'ended_at', 'duration', 'room_id', 'participants'
        )
        read_only_fields = ('id', 'room_id', 'started_at')

class CallListSerializer(serializers.ModelSerializer):
    caller = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    
    class Meta:
        model = Call
        fields = (
            'id', 'caller', 'receiver', 'call_type', 'status', 
            'started_at', 'ended_at', 'duration'
        )

