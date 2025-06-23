# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Mixins réutilisables pour les modèles du Course.
"""

from django.db import models


class MultilingualMixin(models.Model):
    """
    Mixin pour gérer les champs multilingues de manière centralisée.
    Réduit la duplication de code et facilite la maintenance.
    """
    class Meta:
        abstract = True
    
    def get_localized_field(self, field_base_name, target_language='en'):
        """
        Récupère la valeur d'un champ dans la langue demandée.
        Fallback vers l'anglais si la langue demandée n'existe pas.
        """
        field_name = f"{field_base_name}_{target_language}"
        value = getattr(self, field_name, None)
        
        # Fallback vers l'anglais si pas de valeur
        if not value and target_language != 'en':
            value = getattr(self, f"{field_base_name}_en", None)
        
        return value or ""
    
    def get_all_languages_for_field(self, field_base_name):
        """
        Retourne un dictionnaire avec toutes les traductions d'un champ.
        """
        languages = ['en', 'fr', 'es', 'nl']
        return {
            lang: getattr(self, f"{field_base_name}_{lang}", "")
            for lang in languages
        }