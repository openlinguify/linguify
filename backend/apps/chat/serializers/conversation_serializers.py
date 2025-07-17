# backend/chat/serializers/conversation_serializers.py
from rest_framework import serializers
from apps.community.models import Conversation
from ..models import ConversationMessage, Call, CallParticipant
from apps.authentication.serializers.settings_serializers import UserSerializer

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
        fields = ('id', 'call', 'user', 'joined_at', 'left_at', 'is_active')

class CallSerializer(serializers.ModelSerializer):
    participants = CallParticipantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Call
        fields = ('id', 'call_id', 'started_at', 'ended_at', 'is_active', 'participants')