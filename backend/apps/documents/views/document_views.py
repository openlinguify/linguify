from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from ..models import Document, DocumentShare, DocumentVersion, Folder, DocumentComment
from ..serializers import (
    FolderSerializer, DocumentSerializer, DocumentListSerializer,
    DocumentShareSerializer, DocumentVersionSerializer, DocumentCommentSerializer
)
from ..utils import (
    doc_logger, DocumentsError, DocumentPermissionError, DocumentNotFoundError,
    DocumentValidationError, handle_api_errors, log_user_action, 
    validate_document_permission, track_document_activity, PerformanceMonitor
)
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class FolderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing document folders"""
    
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return folders owned by the current user"""
        with PerformanceMonitor('folder_queryset') as monitor:
            queryset = Folder.objects.filter(owner=self.request.user).select_related('owner', 'parent')
            monitor.add_metric('folder_count', queryset.count())
            return queryset
    
    @handle_api_errors
    @log_user_action('create', 'folder')
    def create(self, request, *args, **kwargs):
        """Create a new folder with enhanced logging"""
        doc_logger.log_user_action(
            user=request.user,
            action='create_folder',
            resource_type='folder',
            folder_name=request.data.get('name', 'Unknown')
        )
        return super().create(request, *args, **kwargs)
    
    @handle_api_errors
    @log_user_action('update', 'folder') 
    def update(self, request, *args, **kwargs):
        """Update folder with logging"""
        folder = self.get_object()
        old_name = folder.name
        
        response = super().update(request, *args, **kwargs)
        
        doc_logger.log_user_action(
            user=request.user,
            action='update_folder',
            resource_type='folder',
            resource_id=folder.id,
            old_name=old_name,
            new_name=request.data.get('name', old_name)
        )
        
        return response
    
    @handle_api_errors
    @log_user_action('delete', 'folder')
    def destroy(self, request, *args, **kwargs):
        """Delete folder with safety checks"""
        folder = self.get_object()
        
        # Check if folder has documents
        if folder.documents.exists():
            raise DocumentValidationError(
                "Cannot delete folder that contains documents",
                field='documents',
                value=folder.documents.count()
            )
        
        # Check if folder has subfolders
        if folder.subfolders.exists():
            raise DocumentValidationError(
                "Cannot delete folder that contains subfolders",
                field='subfolders',
                value=folder.subfolders.count()
            )
        
        doc_logger.log_user_action(
            user=request.user,
            action='delete_folder',
            resource_type='folder',
            resource_id=folder.id,
            folder_name=folder.name
        )
        
        return super().destroy(request, *args, **kwargs)
        
    @handle_api_errors
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get documents in a specific folder"""
        folder = self.get_object()
        
        with PerformanceMonitor('folder_documents') as monitor:
            documents = Document.objects.filter(
                folder=folder
            ).filter(
                Q(owner=request.user) | 
                Q(shares__user=request.user, shares__permission_level__in=['view', 'edit', 'admin'])
            ).distinct().select_related('owner', 'last_edited_by')
            
            monitor.add_metric('document_count', documents.count())
            
            serializer = DocumentListSerializer(documents, many=True, context={'request': request})
            
            track_document_activity(
                document=None,
                user=request.user,
                activity_type='view_folder_documents',
                details={'folder_id': folder.id, 'folder_name': folder.name, 'document_count': documents.count()}
            )
            
            return Response(serializer.data)


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing documents with enhanced error handling and logging"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail views"""
        if self.action == 'list':
            return DocumentListSerializer
        return DocumentSerializer
    
    def get_queryset(self):
        """Return documents accessible by the current user"""
        user = self.request.user
        
        with PerformanceMonitor('document_queryset') as monitor:
            # Base queryset: owned documents + shared documents
            queryset = Document.objects.filter(
                Q(owner=user) | 
                Q(shares__user=user)
            ).distinct().select_related(
                'owner', 'last_edited_by', 'folder'
            ).prefetch_related(
                'shares__user', 'shares__shared_by'
            )
            
            # Filter by query parameters
            folder_id = self.request.query_params.get('folder')
            if folder_id:
                try:
                    folder_id = int(folder_id)
                    queryset = queryset.filter(folder_id=folder_id)
                    monitor.add_metric('filtered_by_folder', True)
                except (ValueError, TypeError):
                    doc_logger.log_error(
                        DocumentValidationError("Invalid folder ID", field='folder', value=folder_id),
                        user=user
                    )
                
            search = self.request.query_params.get('search')
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) | 
                    Q(content__icontains=search) |
                    Q(tags__icontains=search)
                )
                monitor.add_metric('search_query', search[:50])  # Limit for privacy
                
            visibility = self.request.query_params.get('visibility')
            if visibility and visibility in ['private', 'shared', 'public']:
                queryset = queryset.filter(visibility=visibility)
                monitor.add_metric('filtered_by_visibility', visibility)
                
            language = self.request.query_params.get('language')
            if language:
                queryset = queryset.filter(language=language)
                monitor.add_metric('filtered_by_language', language)
            
            final_queryset = queryset.order_by('-updated_at')
            monitor.add_metric('result_count', final_queryset.count())
            
            return final_queryset
    
    @handle_api_errors
    @log_user_action('create', 'document')
    def create(self, request, *args, **kwargs):
        """Create a document with enhanced validation and logging"""
        # Validate required fields
        title = request.data.get('title', '').strip()
        if not title:
            raise DocumentValidationError(
                "Document title is required",
                field='title',
                value=title
            )
        
        if len(title) > 255:
            raise DocumentValidationError(
                "Document title too long (max 255 characters)",
                field='title',
                value=len(title)
            )
        
        doc_logger.log_user_action(
            user=request.user,
            action='create_document',
            resource_type='document',
            title=title
        )
        
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Set the owner when creating a document"""
        document = serializer.save(owner=self.request.user, last_edited_by=self.request.user)
        
        track_document_activity(
            document=document,
            user=self.request.user,
            activity_type='document_created',
            details={'content_type': document.content_type, 'visibility': document.visibility}
        )
        
    @handle_api_errors
    @log_user_action('update', 'document')
    def update(self, request, *args, **kwargs):
        """Update document with permission checking and logging"""
        document = self.get_object()
        
        # Validate permissions
        validate_document_permission(request.user, document, 'edit')
        
        # Track changes
        old_title = document.title
        old_content_length = len(document.content) if document.content else 0
        
        response = super().update(request, *args, **kwargs)
        
        # Log the update
        document.refresh_from_db()
        new_content_length = len(document.content) if document.content else 0
        
        track_document_activity(
            document=document,
            user=request.user,
            activity_type='document_updated',
            details={
                'title_changed': old_title != document.title,
                'content_change': new_content_length - old_content_length,
                'old_title': old_title
            }
        )
        
        return response
        
    def perform_update(self, serializer):
        """Track last editor when updating"""
        serializer.save(last_edited_by=self.request.user)
    
    @handle_api_errors
    @log_user_action('delete', 'document')
    def destroy(self, request, *args, **kwargs):
        """Delete document with permission checking and logging"""
        document = self.get_object()
        
        # Only owner can delete
        if document.owner != request.user:
            raise DocumentPermissionError(
                "Only the document owner can delete it",
                user=request.user,
                document=document
            )
        
        # Log deletion before actually deleting
        doc_logger.log_user_action(
            user=request.user,
            action='delete_document',
            resource_type='document',
            resource_id=document.id,
            title=document.title,
            collaborators_count=document.collaborators.count()
        )
        
        track_document_activity(
            document=document,
            user=request.user,
            activity_type='document_deleted',
            details={'title': document.title, 'had_collaborators': document.collaborators.exists()}
        )
        
        return super().destroy(request, *args, **kwargs)
    
    @handle_api_errors
    @log_user_action('view', 'document')
    def retrieve(self, request, *args, **kwargs):
        """Retrieve document with permission checking and activity tracking"""
        document = self.get_object()
        
        # Validate permissions
        validate_document_permission(request.user, document, 'view')
        
        # Track view activity
        track_document_activity(
            document=document,
            user=request.user,
            activity_type='document_viewed',
            details={'content_type': document.content_type}
        )
        
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Create a copy of an existing document"""
        original = self.get_object()
        
        # Create a copy
        duplicate = Document.objects.create(
            title=f"{original.title} (copie)",
            content=original.content,
            content_type=original.content_type,
            folder=original.folder,
            owner=request.user,
            last_edited_by=request.user,
            language=original.language,
            difficulty_level=original.difficulty_level,
            tags=original.tags,
            visibility='private'  # Always start as private
        )
        
        serializer = DocumentSerializer(duplicate, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export document in various formats"""
        document = self.get_object()
        format_type = request.query_params.get('format', 'markdown')
        
        if format_type == 'markdown':
            content = document.content
            content_type = 'text/markdown'
        elif format_type == 'html':
            # Convert markdown to HTML if needed
            if document.content_type == 'markdown':
                import markdown
                content = markdown.markdown(document.content)
            else:
                content = document.content
            content_type = 'text/html'
        else:
            return Response(
                {'error': 'Format non supporté'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'title': document.title,
            'content': content,
            'format': format_type,
            'content_type': content_type
        })


class DocumentShareViewSet(viewsets.ModelViewSet):
    """ViewSet for managing document sharing with enhanced error handling"""
    
    serializer_class = DocumentShareSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return shares for documents accessible by the current user"""
        user = self.request.user
        
        with PerformanceMonitor('share_queryset') as monitor:
            # Get shares for documents owned by user or where user has admin permission
            queryset = DocumentShare.objects.filter(
                Q(document__owner=user) |
                Q(document__shares__user=user, document__shares__permission_level='admin')
            ).distinct().select_related(
                'user', 'shared_by', 'document'
            )
            
            monitor.add_metric('share_count', queryset.count())
            return queryset
    
    @handle_api_errors
    @log_user_action('create', 'document_share')
    def create(self, request, *args, **kwargs):
        """Create a new share with validation and logging"""
        document_id = request.data.get('document')
        user_email = request.data.get('user_email', '').strip()
        
        # Validate required fields
        if not user_email:
            raise DocumentValidationError(
                "User email is required for sharing",
                field='user_email',
                value=user_email
            )
        
        # Check if target user exists
        try:
            target_user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            raise DocumentValidationError(
                f"No user found with email {user_email}",
                field='user_email', 
                value=user_email
            )
        
        # Get document and validate permissions
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            raise DocumentNotFoundError(document_id)
        
        # Check if user can share this document
        can_share = (
            document.owner == request.user or
            document.shares.filter(
                user=request.user, 
                permission_level='admin'
            ).exists()
        )
        
        if not can_share:
            raise DocumentPermissionError(
                "You don't have permission to share this document",
                user=request.user,
                document=document
            )
        
        # Check if already shared with this user
        existing_share = document.shares.filter(user=target_user).first()
        if existing_share:
            raise DocumentValidationError(
                f"Document is already shared with {user_email}",
                field='user_email',
                value=user_email
            )
        
        doc_logger.log_user_action(
            user=request.user,
            action='share_document',
            resource_type='document',
            resource_id=document.id,
            target_user=user_email,
            permission_level=request.data.get('permission_level', 'view')
        )
        
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Set shared_by when creating a share"""
        share = serializer.save(shared_by=self.request.user)
        
        track_document_activity(
            document=share.document,
            user=self.request.user,
            activity_type='document_shared',
            details={
                'shared_with': share.user.email,
                'permission_level': share.permission_level,
                'expires_at': share.expires_at.isoformat() if share.expires_at else None
            }
        )
    
    @handle_api_errors
    @log_user_action('update', 'document_share')
    def update(self, request, *args, **kwargs):
        """Update share permissions with logging"""
        share = self.get_object()
        old_permission = share.permission_level
        
        # Validate permission to modify share
        user = request.user
        can_modify = (
            share.document.owner == user or
            share.document.shares.filter(
                user=user,
                permission_level='admin'
            ).exists()
        )
        
        if not can_modify:
            raise DocumentPermissionError(
                "You don't have permission to modify this share",
                user=user,
                document=share.document
            )
        
        response = super().update(request, *args, **kwargs)
        
        # Log the permission change
        share.refresh_from_db()
        track_document_activity(
            document=share.document,
            user=request.user,
            activity_type='share_permission_changed',
            details={
                'shared_user': share.user.email,
                'old_permission': old_permission,
                'new_permission': share.permission_level
            }
        )
        
        return response
    
    @handle_api_errors
    @log_user_action('delete', 'document_share')
    def destroy(self, request, *args, **kwargs):
        """Revoke document access with logging"""
        share = self.get_object()
        
        # Validate permission to revoke share
        user = request.user
        can_revoke = (
            share.document.owner == user or
            share.shared_by == user or
            share.document.shares.filter(
                user=user,
                permission_level='admin'
            ).exists()
        )
        
        if not can_revoke:
            raise DocumentPermissionError(
                "You don't have permission to revoke this share",
                user=user,
                document=share.document
            )
        
        # Log before deletion
        doc_logger.log_user_action(
            user=request.user,
            action='revoke_share',
            resource_type='document_share',
            resource_id=share.id,
            shared_user=share.user.email,
            document_title=share.document.title
        )
        
        track_document_activity(
            document=share.document,
            user=request.user,
            activity_type='share_revoked',
            details={
                'revoked_user': share.user.email,
                'had_permission': share.permission_level
            }
        )
        
        return super().destroy(request, *args, **kwargs)
    
    @handle_api_errors
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke document access (legacy endpoint)"""
        return self.destroy(request, pk=pk)


class DocumentVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing document versions with enhanced error handling"""
    
    serializer_class = DocumentVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return versions for documents accessible by the current user"""
        user = self.request.user
        
        with PerformanceMonitor('version_queryset') as monitor:
            queryset = DocumentVersion.objects.filter(
                Q(document__owner=user) |
                Q(document__shares__user=user)
            ).distinct().select_related(
                'document', 'created_by'
            ).order_by('-version_number')
            
            monitor.add_metric('version_count', queryset.count())
            return queryset
    
    @handle_api_errors
    @log_user_action('view', 'document_version')
    def retrieve(self, request, *args, **kwargs):
        """Retrieve version with permission checking"""
        version = self.get_object()
        
        # Validate view permission for the document
        validate_document_permission(request.user, version.document, 'view')
        
        track_document_activity(
            document=version.document,
            user=request.user,
            activity_type='version_viewed',
            details={
                'version_number': version.version_number,
                'version_created': version.created_at.isoformat()
            }
        )
        
        return super().retrieve(request, *args, **kwargs)
    
    @handle_api_errors
    @log_user_action('restore', 'document_version')
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore document to this version with comprehensive validation"""
        version = self.get_object()
        document = version.document
        
        # Validate edit permission
        validate_document_permission(request.user, document, 'edit')
        
        # Store old content for tracking
        old_content_length = len(document.content) if document.content else 0
        
        # Restore content
        document.content = version.content
        document.last_edited_by = request.user
        document.save()
        
        # Log the restoration
        doc_logger.log_user_action(
            user=request.user,
            action='restore_version',
            resource_type='document',
            resource_id=document.id,
            version_number=version.version_number,
            document_title=document.title
        )
        
        track_document_activity(
            document=document,
            user=request.user,
            activity_type='version_restored',
            details={
                'restored_version': version.version_number,
                'version_date': version.created_at.isoformat(),
                'content_change': len(version.content) - old_content_length,
                'restored_by': version.created_by.username if version.created_by else 'unknown'
            }
        )
        
        return Response({
            'message': 'Version restaurée avec succès',
            'version_number': version.version_number,
            'document_id': document.id
        })


class DocumentCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing document comments with enhanced error handling"""
    
    serializer_class = DocumentCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return comments for documents accessible by the current user"""
        user = self.request.user
        
        with PerformanceMonitor('comment_queryset') as monitor:
            queryset = DocumentComment.objects.filter(
                Q(document__owner=user) |
                Q(document__shares__user=user)
            ).distinct().select_related(
                'document', 'author', 'resolved_by', 'parent'
            ).prefetch_related('replies')
            
            monitor.add_metric('comment_count', queryset.count())
            return queryset
    
    @handle_api_errors
    @log_user_action('create', 'document_comment')
    def create(self, request, *args, **kwargs):
        """Create comment with validation and logging"""
        document_id = request.data.get('document')
        content = request.data.get('content', '').strip()
        
        # Validate required fields
        if not content:
            raise DocumentValidationError(
                "Comment content is required",
                field='content',
                value=content
            )
        
        if len(content) > 2000:
            raise DocumentValidationError(
                "Comment too long (max 2000 characters)",
                field='content',
                value=len(content)
            )
        
        # Get document and validate permissions
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            raise DocumentNotFoundError(document_id)
        
        # Validate comment permission (view permission required)
        validate_document_permission(request.user, document, 'view')
        
        doc_logger.log_user_action(
            user=request.user,
            action='create_comment',
            resource_type='document',
            resource_id=document.id,
            comment_length=len(content)
        )
        
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Set author when creating comment"""
        comment = serializer.save(author=self.request.user)
        
        track_document_activity(
            document=comment.document,
            user=self.request.user,
            activity_type='comment_added',
            details={
                'comment_id': comment.id,
                'is_reply': comment.parent_id is not None,
                'content_length': len(comment.content)
            }
        )
    
    @handle_api_errors
    @log_user_action('update', 'document_comment')
    def update(self, request, *args, **kwargs):
        """Update comment with permission checking"""
        comment = self.get_object()
        
        # Only author can edit their comments
        if comment.author != request.user:
            raise DocumentPermissionError(
                "You can only edit your own comments",
                user=request.user
            )
        
        # Validate content
        content = request.data.get('content', '').strip()
        if content and len(content) > 2000:
            raise DocumentValidationError(
                "Comment too long (max 2000 characters)",
                field='content',
                value=len(content)
            )
        
        old_content = comment.content
        response = super().update(request, *args, **kwargs)
        
        # Log the update
        comment.refresh_from_db()
        track_document_activity(
            document=comment.document,
            user=request.user,
            activity_type='comment_updated',
            details={
                'comment_id': comment.id,
                'content_changed': old_content != comment.content
            }
        )
        
        return response
    
    @handle_api_errors
    @log_user_action('delete', 'document_comment')
    def destroy(self, request, *args, **kwargs):
        """Delete comment with permission checking"""
        comment = self.get_object()
        
        # Check permissions: author, document owner, or admin
        user = request.user
        can_delete = (
            comment.author == user or
            comment.document.owner == user or
            comment.document.shares.filter(
                user=user,
                permission_level='admin'
            ).exists()
        )
        
        if not can_delete:
            raise DocumentPermissionError(
                "You don't have permission to delete this comment",
                user=user
            )
        
        # Log before deletion
        doc_logger.log_user_action(
            user=request.user,
            action='delete_comment',
            resource_type='document_comment',
            resource_id=comment.id,
            document_title=comment.document.title,
            comment_author=comment.author.username
        )
        
        track_document_activity(
            document=comment.document,
            user=request.user,
            activity_type='comment_deleted',
            details={
                'comment_id': comment.id,
                'original_author': comment.author.username,
                'had_replies': comment.replies.exists()
            }
        )
        
        return super().destroy(request, *args, **kwargs)
    
    @handle_api_errors
    @log_user_action('resolve', 'document_comment')
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark comment as resolved with enhanced validation"""
        comment = self.get_object()
        
        # Check permissions
        user = request.user
        can_resolve = (
            comment.author == user or
            comment.document.owner == user or
            comment.document.shares.filter(
                user=user,
                permission_level='admin'
            ).exists()
        )
        
        if not can_resolve:
            raise DocumentPermissionError(
                "You don't have permission to resolve this comment",
                user=user
            )
        
        if comment.is_resolved:
            raise DocumentValidationError(
                "Comment is already resolved",
                field='is_resolved',
                value=True
            )
        
        comment.resolve(user)
        
        doc_logger.log_user_action(
            user=request.user,
            action='resolve_comment',
            resource_type='document_comment',
            resource_id=comment.id,
            document_title=comment.document.title
        )
        
        track_document_activity(
            document=comment.document,
            user=request.user,
            activity_type='comment_resolved',
            details={
                'comment_id': comment.id,
                'comment_author': comment.author.username
            }
        )
        
        serializer = self.get_serializer(comment)
        return Response(serializer.data)
    
    @handle_api_errors
    @log_user_action('unresolve', 'document_comment')
    @action(detail=True, methods=['post']) 
    def unresolve(self, request, pk=None):
        """Mark comment as unresolved with enhanced validation"""
        comment = self.get_object()
        
        # Check permissions (same as resolve)
        user = request.user
        can_resolve = (
            comment.author == user or
            comment.document.owner == user or
            comment.document.shares.filter(
                user=user,
                permission_level='admin'
            ).exists()
        )
        
        if not can_resolve:
            raise DocumentPermissionError(
                "You don't have permission to modify this comment",
                user=user
            )
        
        if not comment.is_resolved:
            raise DocumentValidationError(
                "Comment is already unresolved",
                field='is_resolved',
                value=False
            )
        
        comment.is_resolved = False
        comment.resolved_by = None
        comment.resolved_at = None
        comment.save()
        
        doc_logger.log_user_action(
            user=request.user,
            action='unresolve_comment',
            resource_type='document_comment',
            resource_id=comment.id,
            document_title=comment.document.title
        )
        
        track_document_activity(
            document=comment.document,
            user=request.user,
            activity_type='comment_unresolved',
            details={
                'comment_id': comment.id,
                'comment_author': comment.author.username
            }
        )
        
        serializer = self.get_serializer(comment)
        return Response(serializer.data)