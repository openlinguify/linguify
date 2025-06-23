from rest_framework import serializers
from apps.authentication.models import User
from .models import Profile, Conversation, ChatMessage, FriendRequest, Post, Comment


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for community features"""
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    native_language_display = serializers.SerializerMethodField()
    target_language_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'avatar', 'native_language', 'target_language', 
                  'native_language_display', 'target_language_display']
    
    def get_name(self, obj):
        return obj.name or obj.username
    
    def get_avatar(self, obj):
        if hasattr(obj, 'get_profile_picture_url'):
            return obj.get_profile_picture_url()
        return None
    
    def get_native_language_display(self, obj):
        if hasattr(obj, 'get_native_language_display'):
            return obj.get_native_language_display()
        return obj.native_language
    
    def get_target_language_display(self, obj):
        if hasattr(obj, 'get_target_language_display'):
            return obj.get_target_language_display()
        return obj.target_language


class ProfileSerializer(serializers.ModelSerializer):
    """Profile serializer for community features"""
    user = UserBasicSerializer(read_only=True)
    friends_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'learning_languages', 'teaching_languages', 
                  'is_online', 'friends_count']
    
    def get_friends_count(self, obj):
        return obj.friends.count()


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    sender = UserBasicSerializer(source='sender.user', read_only=True)
    is_own_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'sender', 'timestamp', 'is_read', 'is_own_message']
    
    def get_is_own_message(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender.user.id == request.user.id
        return False


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    participants = ProfileSerializer(many=True, read_only=True)
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'other_participant', 'last_message', 
                  'unread_count', 'last_message']
    
    def get_other_participant(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                user_profile = Profile.objects.get(user=request.user)
                other_participant = obj.participants.exclude(id=user_profile.id).first()
                if other_participant:
                    return ProfileSerializer(other_participant).data
            except Profile.DoesNotExist:
                pass
        return None
    
    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            return ChatMessageSerializer(last_message, context=self.context).data
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                user_profile = Profile.objects.get(user=request.user)
                return obj.messages.filter(receiver=user_profile, is_read=False).count()
            except Profile.DoesNotExist:
                pass
        return 0


class FriendRequestSerializer(serializers.ModelSerializer):
    """Serializer for friend requests"""
    sender = UserBasicSerializer(read_only=True)
    receiver = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for community posts"""
    author = UserBasicSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at',
                  'likes_count', 'comments_count', 'user_has_liked']
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for post comments"""
    author = UserBasicSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at', 'updated_at',
                  'likes_count', 'user_has_liked']
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False


class LanguagePartnerSerializer(serializers.Serializer):
    """Serializer for language partner recommendations"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.CharField()
    avatar = serializers.URLField(allow_null=True)
    native_language = serializers.CharField(allow_null=True)
    target_language = serializers.CharField(allow_null=True)
    bio = serializers.CharField(allow_null=True)
    teaching_languages = serializers.ListField(allow_null=True)
    learning_languages = serializers.ListField(allow_null=True)
    is_online = serializers.BooleanField()
    compatibility_score = serializers.IntegerField()
    is_mutual_exchange = serializers.BooleanField()
    exchange_type = serializers.CharField()


class FriendSuggestionSerializer(serializers.Serializer):
    """Serializer for friend suggestions"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.CharField()
    avatar = serializers.URLField(allow_null=True)
    native_language = serializers.CharField(allow_null=True)
    target_language = serializers.CharField(allow_null=True)
    bio = serializers.CharField(allow_null=True)
    is_online = serializers.BooleanField()
    suggestion_reasons = serializers.ListField(child=serializers.CharField())