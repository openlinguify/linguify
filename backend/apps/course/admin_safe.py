# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.
from django.contrib import admin
from django import forms
from .models import TheoryContent, ContentLesson
from django.contrib import messages
from django.utils.html import format_html, mark_safe
import logging

logger = logging.getLogger(__name__)

class TheoryContentAdminFormSimple(forms.ModelForm):
    """Formulaire simplifié sans print pour éviter les erreurs Unicode"""
    
    class Meta:
        model = TheoryContent
        fields = '__all__'
    
    def clean(self):
        """Validation sans print"""
        cleaned_data = super().clean()
        
        # Vérifier la ContentLesson
        content_lesson = cleaned_data.get('content_lesson')
        if content_lesson:
            existing = TheoryContent.objects.filter(content_lesson=content_lesson)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                self.add_error(
                    'content_lesson',
                    f"Un contenu théorique existe déjà pour cette leçon."
                )
        
        # Mode JSON simple
        if cleaned_data.get('using_json_format'):
            content = cleaned_data.get('language_specific_content')
            if not content or content == {} or content == "null":
                cleaned_data['language_specific_content'] = {
                    "en": {"content": "Default content", "explanation": "Default explanation"},
                    "fr": {"content": "Contenu par défaut", "explanation": "Explication par défaut"},
                    "es": {"content": "Contenido predeterminado", "explanation": "Explicación predeterminada"},
                    "nl": {"content": "Standaardinhoud", "explanation": "Standaarduitleg"}
                }
        else:
            # Mode traditionnel - valider les champs
            required_fields = ['content_en', 'content_fr', 'explication_en', 'explication_fr']
            for field in required_fields:
                value = cleaned_data.get(field, '').strip()
                if len(value) < 3:
                    self.add_error(field, f"Ce champ doit contenir au moins 3 caractères.")
        
        return cleaned_data

@admin.register(TheoryContent)
class TheoryContentAdminSimple(admin.ModelAdmin):
    form = TheoryContentAdminFormSimple
    list_display = ('id', 'content_lesson', 'using_json_format')
    
    def save_model(self, request, obj, form, change):
        """Sauvegarde simplifiée sans print"""
        try:
            # Mode JSON - définir les valeurs par défaut
            if obj.using_json_format:
                if not obj.language_specific_content or obj.language_specific_content == {}:
                    obj.language_specific_content = {
                        "en": {"content": "Content", "explanation": "Explanation"},
                        "fr": {"content": "Contenu", "explanation": "Explication"},
                        "es": {"content": "Contenido", "explanation": "Explicación"},
                        "nl": {"content": "Inhoud", "explanation": "Uitleg"}
                    }
                
                # Synchroniser avec les champs traditionnels
                for lang in ["en", "fr", "es", "nl"]:
                    if lang in obj.language_specific_content:
                        content_data = obj.language_specific_content[lang]
                        if isinstance(content_data, dict):
                            setattr(obj, f'content_{lang}', content_data.get('content', f'Content {lang}'))
                            setattr(obj, f'explication_{lang}', content_data.get('explanation', f'Explanation {lang}'))
            
            obj.save()
            messages.success(request, "Le contenu théorique a été créé avec succès!")
            
        except Exception as e:
            messages.error(request, f"Erreur : {str(e)}")
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrer les ContentLessons disponibles"""
        if db_field.name == 'content_lesson':
            used_lessons = TheoryContent.objects.values_list('content_lesson_id', flat=True)
            kwargs['queryset'] = ContentLesson.objects.exclude(id__in=used_lessons)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)