from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Document, DocumentShare, DocumentVersion, Folder, DocumentComment
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for document sharing"""
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'name']
        
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class FolderSerializer(serializers.ModelSerializer):
    """Serializer for document folders"""
    owner = UserBasicSerializer(read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    documents_count = serializers.SerializerMethodField()
    subfolders_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Folder
        fields = [
            'id', 'name', 'description', 'owner', 'parent', 'parent_name',
            'created_at', 'updated_at', 'documents_count', 'subfolders_count'
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']
        
    def get_documents_count(self, obj):
        return obj.documents.count()
        
    def get_subfolders_count(self, obj):
        return obj.subfolders.count()
        
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class DocumentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for document lists"""
    owner = UserBasicSerializer(read_only=True)
    last_edited_by = UserBasicSerializer(read_only=True)
    folder_name = serializers.CharField(source='folder.name', read_only=True)
    tags_list = serializers.ReadOnlyField(source='get_tags_list')
    collaborators_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'content_type', 'visibility', 'language', 
            'difficulty_level', 'tags_list', 'owner', 'last_edited_by',
            'folder', 'folder_name', 'created_at', 'updated_at',
            'collaborators_count', 'comments_count'
        ]
        
    def get_collaborators_count(self, obj):
        return obj.collaborators.count()
        
    def get_comments_count(self, obj):
        return obj.comments.count()


class DocumentSerializer(serializers.ModelSerializer):
    """Full serializer for document details"""
    owner = UserBasicSerializer(read_only=True)
    last_edited_by = UserBasicSerializer(read_only=True)
    folder_name = serializers.CharField(source='folder.name', read_only=True)
    tags_list = serializers.ReadOnlyField(source='get_tags_list')
    collaborators_info = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_share = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'content', 'content_type', 'visibility', 
            'language', 'difficulty_level', 'tags', 'tags_list',
            'owner', 'last_edited_by', 'folder', 'folder_name',
            'created_at', 'updated_at', 'collaborators_info',
            'can_edit', 'can_share', 'can_delete'
        ]
        read_only_fields = ['owner', 'last_edited_by', 'created_at', 'updated_at']
        
    def get_collaborators_info(self, obj):
        """Get detailed collaborator information"""
        shares = obj.shares.select_related('user').all()
        return [
            {
                'user': UserBasicSerializer(share.user).data,
                'permission_level': share.permission_level,
                'shared_at': share.shared_at,
                'shared_by': UserBasicSerializer(share.shared_by).data
            }
            for share in shares
        ]
        
    def get_can_edit(self, obj):
        """Check if current user can edit this document"""
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
            
        # Owner can always edit
        if obj.owner == user:
            return True
            
        # Check share permissions
        try:
            share = obj.shares.get(user=user)
            return share.permission_level in ['edit', 'admin'] and not share.is_expired()
        except DocumentShare.DoesNotExist:
            return False
            
    def get_can_share(self, obj):
        """Check if current user can share this document"""
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
            
        # Owner can always share
        if obj.owner == user:
            return True
            
        # Admin collaborators can share
        try:
            share = obj.shares.get(user=user)
            return share.permission_level == 'admin' and not share.is_expired()
        except DocumentShare.DoesNotExist:
            return False
            
    def get_can_delete(self, obj):
        """Check if current user can delete this document"""
        user = self.context['request'].user
        return obj.owner == user
        
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        validated_data['last_edited_by'] = self.context['request'].user
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        # Track who made the edit
        validated_data['last_edited_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class DocumentShareSerializer(serializers.ModelSerializer):
    """Serializer for document sharing"""
    user = UserBasicSerializer(read_only=True)
    shared_by = UserBasicSerializer(read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = DocumentShare
        fields = [
            'id', 'document', 'user', 'user_id', 'permission_level',
            'shared_by', 'shared_at', 'expires_at', 'document_title',
            'is_expired'
        ]
        read_only_fields = ['shared_by', 'shared_at']
        
    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        validated_data['user'] = User.objects.get(id=user_id)
        validated_data['shared_by'] = self.context['request'].user
        return super().create(validated_data)
        
    def validate_user_id(self, value):
        """Validate that the user exists"""
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur introuvable")
        return value
        
    def validate(self, data):
        """Validate sharing constraints"""
        # Don't allow sharing with the owner
        user_id = data.get('user_id')
        document = data.get('document')
        
        if user_id and document and document.owner.id == user_id:
            raise serializers.ValidationError({
                'user_id': "Impossible de partager un document avec son propriétaire"
            })
            
        return data


class DocumentVersionSerializer(serializers.ModelSerializer):
    """Serializer for document versions"""
    created_by = UserBasicSerializer(read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = DocumentVersion
        fields = [
            'id', 'document', 'document_title', 'content', 'version_number',
            'created_by', 'created_at', 'notes'
        ]
        read_only_fields = ['created_by', 'created_at', 'version_number']


class DocumentCommentSerializer(serializers.ModelSerializer):
    """Serializer for document comments"""
    author = UserBasicSerializer(read_only=True)
    resolved_by = UserBasicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    can_resolve = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentComment
        fields = [
            'id', 'document', 'author', 'content', 'position_start', 
            'position_end', 'parent', 'created_at', 'updated_at',
            'is_resolved', 'resolved_by', 'resolved_at', 'replies',
            'can_resolve'
        ]
        read_only_fields = [
            'author', 'created_at', 'updated_at', 'resolved_by', 'resolved_at'
        ]
        
    def get_replies(self, obj):
        """Get nested replies"""
        if obj.replies.exists():
            return DocumentCommentSerializer(
                obj.replies.all(), 
                many=True, 
                context=self.context
            ).data
        return []
        
    def get_can_resolve(self, obj):
        """Check if current user can resolve this comment"""
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
            
        # Author can resolve their own comments
        if obj.author == user:
            return True
            
        # Document owner can resolve any comment
        if obj.document.owner == user:
            return True
            
        # Admin collaborators can resolve comments
        try:
            share = obj.document.shares.get(user=user)
            return share.permission_level == 'admin' and not share.is_expired()
        except DocumentShare.DoesNotExist:
            return False
            
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)