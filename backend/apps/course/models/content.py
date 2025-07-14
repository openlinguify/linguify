# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Modèles de contenu pour l'application Course.
Contient TheoryContent et autres contenus pédagogiques.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .core import ContentLesson


class TheoryContent(models.Model):
    """Contenu théorique d'une leçon."""
    
    content_lesson = models.OneToOneField(ContentLesson, on_delete=models.CASCADE, related_name='theory_content')
    content_en = models.JSONField(default=dict, help_text="Theory content in English")
    content_fr = models.JSONField(default=dict, help_text="Theory content in French") 
    content_es = models.JSONField(default=dict, help_text="Theory content in Spanish")
    content_nl = models.JSONField(default=dict, help_text="Theory content in Dutch")
    available_languages = models.JSONField(default=list, help_text="List of available languages for this theory")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'course'
        verbose_name = _("Theory Content")
        verbose_name_plural = _("Theory Contents")

    def __str__(self):
        return f"Theory: {self.content_lesson.title_en}"

    def get_content_for_language(self, language='en'):
        """Récupère le contenu théorique pour une langue spécifique."""
        content_field = f'content_{language}'
        content = getattr(self, content_field, {})
        
        # Fallback vers l'anglais si la langue demandée n'existe pas
        if not content and language != 'en':
            content = self.content_en
            
        return content

    def is_language_available(self, language):
        """Vérifie si une langue est disponible pour ce contenu."""
        return language in self.available_languages

    def add_language_support(self, language):
        """Ajoute le support d'une langue."""
        if language not in self.available_languages:
            self.available_languages.append(language)
            self.save(update_fields=['available_languages'])

    def remove_language_support(self, language):
        """Supprime le support d'une langue."""
        if language in self.available_languages:
            self.available_languages.remove(language)
            # Vider aussi le contenu de cette langue
            setattr(self, f'content_{language}', {})
            self.save()

    def get_all_available_content(self):
        """Retourne tout le contenu disponible dans toutes les langues."""
        content = {}
        for language in self.available_languages:
            content[language] = self.get_content_for_language(language)
        return content

    def update_available_languages(self):
        """Met à jour automatiquement la liste des langues disponibles."""
        available = []
        for lang in ['en', 'fr', 'es', 'nl']:
            content = getattr(self, f'content_{lang}', {})
            if content:  # Si le contenu n'est pas vide
                available.append(lang)
        
        self.available_languages = available
        self.save(update_fields=['available_languages'])

    def save(self, *args, **kwargs):
        """Surcharge de save pour mettre à jour automatiquement les langues disponibles."""
        super().save(*args, **kwargs)
        
        # Mettre à jour les langues disponibles après sauvegarde
        if 'update_fields' not in kwargs or 'available_languages' not in kwargs.get('update_fields', []):
            self.update_available_languages()