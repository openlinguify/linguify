from django.contrib import admin
from .models import DocumentUpload


@admin.register(DocumentUpload)
class DocumentUploadAdmin(admin.ModelAdmin):
    list_display = [
        'original_filename',
        'user',
        'document_type',
        'status',
        'flashcards_generated_count',
        'created_at',
        'file_size_mb',
    ]
    list_filter = [
        'status',
        'document_type',
        'created_at',
    ]
    search_fields = [
        'original_filename',
        'user__username',
        'user__email',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'processed_at',
        'file_size_mb',
        'processing_duration',
    ]
    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'deck', 'status')
        }),
        ('Fichier', {
            'fields': (
                'file',
                'original_filename',
                'file_size',
                'file_size_mb',
                'document_type',
                'mime_type',
            )
        }),
        ('Extraction', {
            'fields': (
                'extracted_text',
                'text_extraction_method',
            )
        }),
        ('Résultats', {
            'fields': (
                'flashcards_generated_count',
                'generation_params',
            )
        }),
        ('Erreurs', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': (
                'created_at',
                'updated_at',
                'processed_at',
                'processing_duration',
            )
        }),
    )

    def file_size_mb(self, obj):
        return f"{obj.file_size_mb} Mo"
    file_size_mb.short_description = "Taille"
