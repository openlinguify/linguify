from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class ConversationTopic(models.Model):
    """Sujet de conversation disponible pour les conversations AI."""
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('fr', _('French')),
        ('es', _('Spanish')),
        ('de', _('German')),
        ('it', _('Italian')),
        ('pt', _('Portuguese')),
        ('nl', _('Dutch')),
        ('ru', _('Russian')),
        ('zh', _('Chinese')),
        ('ja', _('Japanese')),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    context = models.TextField(help_text=_("Context information to provide to the AI"))
    example_conversation = models.TextField(blank=True, null=True, help_text=_("Example conversation to guide the AI"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Conversation Topic")
        verbose_name_plural = _("Conversation Topics")
        ordering = ['language', 'difficulty', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_language_display()} - {self.get_difficulty_display()})"


class AIConversation(models.Model):
    """Représente une session de conversation avec l'AI."""
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('paused', _('Paused')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_conversations")
    topic = models.ForeignKey(ConversationTopic, on_delete=models.CASCADE, related_name="conversations")
    language = models.CharField(max_length=10, choices=ConversationTopic.LANGUAGE_CHOICES)
    ai_persona = models.TextField(help_text=_("Persona instruction for the AI"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    feedback_summary = models.TextField(blank=True, null=True, help_text=_("Summary of common mistakes and feedback"))
    
    class Meta:
        verbose_name = _("AI Conversation")
        verbose_name_plural = _("AI Conversations")
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"Conversation: {self.user.username} - {self.topic.name}"
    
    @property
    def message_count(self):
        return self.messages.count()
    
    @property
    def duration_minutes(self):
        if self.status == 'completed' and self.messages.exists():
            first_message = self.messages.order_by('created_at').first()
            last_message = self.messages.order_by('-created_at').first()
            if first_message and last_message:
                delta = last_message.created_at - first_message.created_at
                return round(delta.total_seconds() / 60, 1)
        return 0


class ConversationMessage(models.Model):
    """Message within an AI conversation."""
    MESSAGE_TYPE_CHOICES = [
        ('user', _('User')),
        ('ai', _('AI')),
        ('system', _('System')),
    ]
    
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name="messages")
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Pour le tracking des détails linguistiques
    word_count = models.IntegerField(default=0)
    detected_grammar_errors = models.TextField(blank=True, null=True)
    detected_vocabulary_level = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        verbose_name = _("Conversation Message")
        verbose_name_plural = _("Conversation Messages")
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.get_message_type_display()}: {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        # Calculer le nombre de mots
        if self.content:
            self.word_count = len(self.content.split())
        super().save(*args, **kwargs)


class ConversationFeedback(models.Model):
    """Feedback et corrections pour un message de conversation."""
    CORRECTION_TYPE_CHOICES = [
        ('grammar', _('Grammar')),
        ('vocabulary', _('Vocabulary')),
        ('pronunciation', _('Pronunciation')),
        ('context', _('Context')),
        ('fluency', _('Fluency')),
    ]
    
    message = models.ForeignKey(ConversationMessage, on_delete=models.CASCADE, related_name="feedback")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    correction_type = models.CharField(max_length=20, choices=CORRECTION_TYPE_CHOICES)
    corrected_content = models.TextField()
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Conversation Feedback")
        verbose_name_plural = _("Conversation Feedback")
        ordering = ['message', 'created_at']
    
    def __str__(self):
        return f"Feedback: {self.correction_type} on {self.message}"