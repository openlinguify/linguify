from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Document, DocumentShare, DocumentVersion, Folder, DocumentComment


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    """Admin interface for document folders"""
    
    list_display = ['name', 'owner', 'parent', 'documents_count', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'description', 'owner__username']
    autocomplete_fields = ['owner', 'parent']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Information générale', {
            'fields': ('name', 'description', 'owner', 'parent')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def documents_count(self, obj):
        count = obj.documents.count()
        if count > 0:
            url = reverse('admin:documents_document_changelist') + f'?folder__id__exact={obj.id}'
            return format_html('<a href="{}">{} documents</a>', url, count)
        return '0 documents'
    documents_count.short_description = 'Documents'


class DocumentShareInline(admin.TabularInline):
    """Inline admin for document shares"""
    model = DocumentShare
    extra = 0
    autocomplete_fields = ['user', 'shared_by']
    readonly_fields = ['shared_at']


class DocumentVersionInline(admin.TabularInline):
    """Inline admin for document versions"""
    model = DocumentVersion
    extra = 0
    readonly_fields = ['version_number', 'created_at', 'created_by']
    fields = ['version_number', 'created_by', 'created_at', 'notes']
    
    def has_add_permission(self, request, obj=None):
        return False  # Versions are created automatically


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for documents"""
    
    list_display = [
        'title', 'owner', 'visibility', 'content_type', 
        'collaborators_count', 'last_edited_by', 'updated_at'
    ]
    list_filter = [
        'content_type', 'visibility', 'language', 'difficulty_level',
        'created_at', 'updated_at'
    ]
    search_fields = ['title', 'content', 'tags', 'owner__username']
    autocomplete_fields = ['owner', 'last_edited_by', 'folder']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [DocumentShareInline, DocumentVersionInline]
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'content', 'content_type')
        }),
        ('Organisation', {
            'fields': ('folder', 'visibility', 'tags')
        }),
        ('Propriétés éducatives', {
            'fields': ('language', 'difficulty_level'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('owner', 'last_edited_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def collaborators_count(self, obj):
        count = obj.collaborators.count()
        if count > 0:
            return format_html('{} collaborateurs', count)
        return 'Aucun collaborateur'
    collaborators_count.short_description = 'Collaborateurs'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('owner', 'last_edited_by', 'folder')


@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    """Admin interface for document shares"""
    
    list_display = [
        'document', 'user', 'permission_level', 
        'shared_by', 'shared_at', 'expires_at', 'is_expired'
    ]
    list_filter = [
        'permission_level', 'shared_at', 'expires_at'
    ]
    search_fields = [
        'document__title', 'user__username', 'shared_by__username'
    ]
    autocomplete_fields = ['document', 'user', 'shared_by']
    readonly_fields = ['shared_at']
    
    def is_expired(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Expiré</span>')
        return format_html('<span style="color: green;">Actif</span>')
    is_expired.short_description = 'Statut'


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    """Admin interface for document versions"""
    
    list_display = [
        'document', 'version_number', 'created_by', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['document__title', 'created_by__username', 'notes']
    autocomplete_fields = ['document', 'created_by']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Version', {
            'fields': ('document', 'version_number', 'notes')
        }),
        ('Contenu', {
            'fields': ('content',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )


class DocumentCommentReplyInline(admin.TabularInline):
    """Inline admin for comment replies"""
    model = DocumentComment
    fk_name = 'parent'
    extra = 0
    fields = ['author', 'content', 'created_at', 'is_resolved']
    readonly_fields = ['created_at']


@admin.register(DocumentComment)
class DocumentCommentAdmin(admin.ModelAdmin):
    """Admin interface for document comments"""
    
    list_display = [
        'document', 'author', 'short_content', 'is_resolved', 
        'created_at', 'resolved_by'
    ]
    list_filter = [
        'is_resolved', 'created_at', 'resolved_at'
    ]
    search_fields = [
        'document__title', 'author__username', 'content'
    ]
    autocomplete_fields = ['document', 'author', 'parent', 'resolved_by']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    inlines = [DocumentCommentReplyInline]
    
    fieldsets = (
        ('Commentaire', {
            'fields': ('document', 'author', 'content', 'parent')
        }),
        ('Position', {
            'fields': ('position_start', 'position_end'),
            'classes': ('collapse',)
        }),
        ('Résolution', {
            'fields': ('is_resolved', 'resolved_by', 'resolved_at'),
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def short_content(self, obj):
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    short_content.short_description = 'Contenu'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'document', 'author', 'parent', 'resolved_by'
        )


# Custom admin site configuration
admin.site.site_header = 'Administration Documents Linguify'
admin.site.site_title = 'Documents Admin'
admin.site.index_title = 'Gestion des Documents'