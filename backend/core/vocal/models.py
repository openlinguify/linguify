from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class VoiceInteraction(models.Model):
    """Modèle pour stocker les interactions vocales des utilisateurs"""
    
    INTERACTION_TYPES = [
        ('speech_to_text', 'Speech to Text'),
        ('text_to_speech', 'Text to Speech'),
        ('voice_command', 'Voice Command'),
        ('pronunciation', 'Pronunciation Practice'),
    ]
    
    COMMAND_TYPES = [
        ('navigation', 'Navigation'),
        ('learning', 'Learning'),
        ('practice', 'Practice'),
        ('quiz', 'Quiz'),
        ('general', 'General'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voice_interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    command_type = models.CharField(max_length=20, choices=COMMAND_TYPES, null=True, blank=True)
    
    # Données audio et texte
    input_text = models.TextField(blank=True, help_text="Texte de l'entrée utilisateur")
    output_text = models.TextField(blank=True, help_text="Texte de la réponse générée")
    audio_duration = models.FloatField(null=True, blank=True, help_text="Durée audio en secondes")
    
    # Métadonnées de reconnaissance
    confidence_score = models.FloatField(null=True, blank=True, help_text="Score de confiance (0-1)")
    language_code = models.CharField(max_length=10, help_text="Code de langue (ex: fr-FR)")
    
    # Contexte de l'interaction
    session_id = models.CharField(max_length=100, blank=True, help_text="ID de session de conversation")
    context_data = models.JSONField(default=dict, blank=True, help_text="Données de contexte JSON")
    
    # Métriques et suivi
    response_time = models.FloatField(null=True, blank=True, help_text="Temps de réponse en millisecondes")
    success = models.BooleanField(default=True, help_text="Si l'interaction a réussi")
    error_message = models.TextField(blank=True, help_text="Message d'erreur si échec")
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['interaction_type', '-created_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class VoicePreference(models.Model):
    """Préférences vocales spécifiques à l'utilisateur"""
    
    VOICE_SPEEDS = [
        ('slow', 'Lent (120 mots/min)'),
        ('normal', 'Normal (180 mots/min)'),
        ('fast', 'Rapide (240 mots/min)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='voice_preference')
    
    # Préférences TTS
    preferred_voice_speed = models.CharField(max_length=10, choices=VOICE_SPEEDS, default='normal')
    preferred_voice_pitch = models.IntegerField(default=50, help_text="Hauteur de voix (0-100)")
    tts_enabled = models.BooleanField(default=True, help_text="Activer la synthèse vocale")
    
    # Préférences STT
    auto_listen = models.BooleanField(default=False, help_text="Écoute automatique activée")
    noise_suppression = models.BooleanField(default=True, help_text="Suppression du bruit")
    sensitivity = models.IntegerField(default=70, help_text="Sensibilité du micro (0-100)")
    
    # Langues et dialectes
    preferred_accent = models.CharField(max_length=10, blank=True, help_text="Accent préféré (ex: en-US, en-GB)")
    
    # Fonctionnalités avancées
    voice_commands_enabled = models.BooleanField(default=True, help_text="Commandes vocales activées")
    pronunciation_feedback = models.BooleanField(default=True, help_text="Feedback de prononciation")
    conversation_mode = models.BooleanField(default=False, help_text="Mode conversation continue")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Préférences vocales de {self.user.username}"

class VoiceCommand(models.Model):
    """Commandes vocales personnalisées"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voice_commands')
    
    # Définition de la commande
    trigger_phrase = models.CharField(max_length=200, help_text="Phrase qui déclenche la commande")
    action_type = models.CharField(max_length=50, help_text="Type d'action à exécuter")
    action_params = models.JSONField(default=dict, help_text="Paramètres de l'action")
    
    # Métadonnées
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0, help_text="Nombre d'utilisations")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'trigger_phrase']
    
    def __str__(self):
        return f"{self.user.username}: '{self.trigger_phrase}' -> {self.action_type}"

class ConversationSession(models.Model):
    """Sessions de conversation vocale"""
    
    SESSION_TYPES = [
        ('practice', 'Pratique'),
        ('lesson', 'Leçon'),
        ('quiz', 'Quiz'),
        ('free_talk', 'Conversation libre'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_sessions')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    
    # Détails de la session
    title = models.CharField(max_length=200, blank=True)
    topic = models.CharField(max_length=100, blank=True, help_text="Sujet de conversation")
    language_practiced = models.CharField(max_length=10, help_text="Langue pratiquée")
    
    # Métriques de session
    total_interactions = models.IntegerField(default=0)
    total_duration = models.IntegerField(default=0, help_text="Durée totale en secondes")
    average_confidence = models.FloatField(null=True, blank=True)
    
    # État de la session
    is_active = models.BooleanField(default=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.session_type} - {self.created_at.strftime('%Y-%m-%d')}"
