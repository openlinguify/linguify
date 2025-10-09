from django.db import models
from django.conf import settings
from django.utils import timezone


class DocumentUpload(models.Model):
    """
    Modèle pour stocker les documents uploadés (PDF, images, texte)
    avant génération des flashcards
    """
    DOCUMENT_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('image', 'Image'),
        ('text', 'Texte'),
        ('other', 'Autre'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_uploads'
    )
    deck = models.ForeignKey(
        'revision.FlashcardDeck',
        on_delete=models.CASCADE,
        related_name='uploaded_documents',
        null=True,
        blank=True,
        help_text="Deck cible pour les flashcards générées"
    )

    # Informations sur le fichier
    file = models.FileField(
        upload_to='ai_documents/uploads/%Y/%m/%d/',
        help_text="Fichier uploadé (PDF, image, texte)"
    )
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(
        help_text="Taille du fichier en octets"
    )
    document_type = models.CharField(
        max_length=10,
        choices=DOCUMENT_TYPE_CHOICES,
        default='other'
    )
    mime_type = models.CharField(max_length=100, blank=True)

    # Métadonnées de traitement
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    extracted_text = models.TextField(
        blank=True,
        help_text="Texte extrait du document"
    )
    text_extraction_method = models.CharField(
        max_length=50,
        blank=True,
        help_text="Méthode utilisée (PyMuPDF, OCR, etc.)"
    )

    # Statistiques de génération
    flashcards_generated_count = models.PositiveIntegerField(
        default=0,
        help_text="Nombre de flashcards générées à partir de ce document"
    )

    # Métadonnées temporelles
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de fin de traitement"
    )

    # Gestion des erreurs
    error_message = models.TextField(
        blank=True,
        help_text="Message d'erreur en cas d'échec"
    )

    # Paramètres de génération IA
    generation_params = models.JSONField(
        default=dict,
        blank=True,
        help_text="Paramètres utilisés pour la génération (modèle IA, température, etc.)"
    )

    class Meta:
        app_label = 'ai_documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['deck']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.get_status_display()})"

    def mark_as_processing(self):
        """Marque le document comme en cours de traitement"""
        self.status = 'processing'
        self.save(update_fields=['status', 'updated_at'])

    def mark_as_completed(self, flashcards_count=0):
        """Marque le document comme traité avec succès"""
        self.status = 'completed'
        self.processed_at = timezone.now()
        self.flashcards_generated_count = flashcards_count
        self.save(update_fields=[
            'status',
            'processed_at',
            'flashcards_generated_count',
            'updated_at'
        ])

    def mark_as_failed(self, error_message=''):
        """Marque le document comme échoué"""
        self.status = 'failed'
        self.error_message = error_message
        self.processed_at = timezone.now()
        self.save(update_fields=[
            'status',
            'error_message',
            'processed_at',
            'updated_at'
        ])

    @property
    def file_size_mb(self):
        """Retourne la taille du fichier en Mo"""
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def processing_duration(self):
        """Calcule la durée de traitement"""
        if self.processed_at and self.created_at:
            return (self.processed_at - self.created_at).total_seconds()
        return None
