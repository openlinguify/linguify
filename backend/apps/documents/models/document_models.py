from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class Folder(models.Model):
    """Organization folder for documents"""
    
    name = models.CharField(max_length=255, verbose_name="Nom du dossier")
    description = models.TextField(blank=True, verbose_name="Description")
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='owned_folders',
        verbose_name="Propriétaire"
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='subfolders',
        verbose_name="Dossier parent"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Dossier"
        verbose_name_plural = "Dossiers"
        ordering = ['name']
        
    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('documents:folder_detail', kwargs={'pk': self.pk})


class Document(models.Model):
    """Main document model for collaborative editing"""
    
    CONTENT_TYPE_CHOICES = [
        ('markdown', 'Markdown'),
        ('html', 'HTML'),
        ('plaintext', 'Texte simple'),
    ]
    
    VISIBILITY_CHOICES = [
        ('private', 'Privé'),
        ('shared', 'Partagé'),
        ('public', 'Public'),
    ]
    
    title = models.CharField(max_length=255, verbose_name="Titre")
    content = models.TextField(blank=True, verbose_name="Contenu")
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='markdown',
        verbose_name="Type de contenu"
    )
    
    # Organization
    folder = models.ForeignKey(
        Folder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name="Dossier"
    )
    
    # Ownership and permissions
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_documents',
        verbose_name="Propriétaire"
    )
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='private',
        verbose_name="Visibilité"
    )
    
    # Collaboration
    collaborators = models.ManyToManyField(
        User,
        through='DocumentShare',
        through_fields=('document', 'user'),
        related_name='shared_documents',
        blank=True,
        verbose_name="Collaborateurs"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    last_edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='last_edited_documents',
        verbose_name="Dernière modification par"
    )
    
    # Educational features
    language = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Langue du document"
    )
    difficulty_level = models.CharField(
        max_length=2,
        choices=[
            ('A1', 'A1 - Débutant'),
            ('A2', 'A2 - Élémentaire'),
            ('B1', 'B1 - Intermédiaire'),
            ('B2', 'B2 - Intermédiaire supérieur'),
            ('C1', 'C1 - Avancé'),
            ('C2', 'C2 - Maîtrise'),
        ],
        blank=True,
        verbose_name="Niveau de difficulté"
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Tags séparés par des virgules",
        verbose_name="Tags"
    )
    
    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-updated_at']
        permissions = [
            ('share_document', 'Can share document'),
        ]
        
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return reverse('documents:document_detail', kwargs={'pk': self.pk})
        
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
        
    def save(self, *args, **kwargs):
        # Update last_edited_by if content has changed
        if self.pk:
            old_doc = Document.objects.get(pk=self.pk)
            if old_doc.content != self.content:
                # Create a version snapshot before saving
                DocumentVersion.objects.create(
                    document=self,
                    content=old_doc.content,
                    version_number=self.versions.count() + 1,
                    created_by=self.last_edited_by or self.owner
                )
        super().save(*args, **kwargs)


class DocumentShare(models.Model):
    """Sharing permissions for documents"""
    
    PERMISSION_CHOICES = [
        ('view', 'Lecture seule'),
        ('edit', 'Édition'),
        ('admin', 'Administration'),
    ]
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='shares',
        verbose_name="Document"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='document_shares',
        verbose_name="Utilisateur"
    )
    permission_level = models.CharField(
        max_length=10,
        choices=PERMISSION_CHOICES,
        default='view',
        verbose_name="Niveau de permission"
    )
    
    shared_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shared_documents_by',
        verbose_name="Partagé par"
    )
    shared_at = models.DateTimeField(auto_now_add=True, verbose_name="Partagé le")
    
    # Optional expiration
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expire le"
    )
    
    class Meta:
        verbose_name = "Partage de document"
        verbose_name_plural = "Partages de documents"
        unique_together = ['document', 'user']
        ordering = ['-shared_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.document.title} ({self.permission_level})"
        
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class DocumentVersion(models.Model):
    """Version history for documents"""
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name="Document"
    )
    content = models.TextField(verbose_name="Contenu de la version")
    version_number = models.PositiveIntegerField(verbose_name="Numéro de version")
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Créé par"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    # Optional version notes
    notes = models.TextField(
        blank=True,
        verbose_name="Notes de version"
    )
    
    class Meta:
        verbose_name = "Version de document"
        verbose_name_plural = "Versions de documents"
        ordering = ['-version_number']
        unique_together = ['document', 'version_number']
        
    def __str__(self):
        return f"{self.document.title} - v{self.version_number}"


class DocumentComment(models.Model):
    """Comments and annotations on documents"""
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Document"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='document_comments',
        verbose_name="Auteur"
    )
    
    content = models.TextField(verbose_name="Commentaire")
    
    # Position in document (for inline comments)
    position_start = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Position de début"
    )
    position_end = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Position de fin"
    )
    
    # Threading for replies
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name="Commentaire parent"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    # Status
    is_resolved = models.BooleanField(default=False, verbose_name="Résolu")
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_comments',
        verbose_name="Résolu par"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Résolu le"
    )
    
    class Meta:
        verbose_name = "Commentaire de document"
        verbose_name_plural = "Commentaires de documents"
        ordering = ['created_at']
        
    def __str__(self):
        return f"Commentaire de {self.author.username} sur {self.document.title}"
        
    def resolve(self, user):
        """Mark comment as resolved"""
        self.is_resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.save()