from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Exemple de modèle pour Language Learning
class LanguagelearningItem(models.Model):
    """Modèle de base pour Language Learning"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='language_learning_items')
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Language Learning Item"
        verbose_name_plural = "Language Learning Items"
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title

LIST_OF_LANGUAGES_TO_LEARN = [
    'ENGLISH',
    'FRENCH',
    'SPAIN',
    'DUTCH'
    ]

class learning_path(models.Model):
    pass