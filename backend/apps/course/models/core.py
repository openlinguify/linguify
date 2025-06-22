# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Modèles principaux de l'application Course.
Contient Unit, Lesson et ContentLesson.
"""

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from .mixins import MultilingualMixin

# Type activity choices
TYPE_ACTIVITY = [
    ('Theory', 'Theory'),
    ('Vocabulary', 'Vocabulary'),
    ('Grammar', 'Grammar'),
    ('Listening', 'Listening'),
    ('Speaking', 'Speaking'),
    ('Reading', 'Reading'),
    ('Writing', 'Writing'),
    ('Test', 'Test'),
]


class Unit(MultilingualMixin):
    """
    Unité de cours pour l'apprentissage des langues.
    Utilise MultilingualMixin pour optimiser la gestion des traductions.
    """
    LEVEL_CHOICES = [
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
        ('C1', 'C1'),
        ('C2', 'C2'),
    ]
    
    title_en = models.CharField(max_length=100, blank=False, null=False)
    title_fr = models.CharField(max_length=100, blank=False, null=False)
    title_es = models.CharField(max_length=100, blank=False, null=False)
    title_nl = models.CharField(max_length=100, blank=False, null=False)
    description_en = models.TextField(null=True, blank=True)
    description_fr = models.TextField(null=True, blank=True)
    description_es = models.TextField(null=True, blank=True)
    description_nl = models.TextField(null=True, blank=True)
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, blank=False, null=False)
    order = models.PositiveIntegerField(blank=False, null=False, default=1)

    class Meta:
        app_label = 'course'
        ordering = ['order']
    
    def get_formatted_titles(self):
        titles = {
            'EN': self.title_en,
            'FR': self.title_fr,
            'ES': self.title_es,
            'NL': self.title_nl
        }
        return ' | '.join(
            f"{lang}: {title[:20]}..." if len(title) > 20 else f"{lang}: {title}"
            for lang, title in titles.items()
        )

    def __str__(self):
        unit_info = f"Unit {self.order:02d}".ljust(15)
        level_info = f"[{self.level}]".ljust(5)
        
        # Format spécifique avec troncature exacte à 20 caractères
        titles = {
            'EN': self.title_en[:20] + "..." if len(self.title_en) > 20 else self.title_en,
            'FR': self.title_fr[:20] + "..." if len(self.title_fr) > 20 else self.title_fr,
            'ES': self.title_es[:20] + "..." if len(self.title_es) > 20 else self.title_es,
            'NL': self.title_nl[:20] + "..." if len(self.title_nl) > 20 else self.title_nl
        }
        
        formatted_titles = ' | '.join(f"{lang}: {title}" for lang, title in titles.items())
        return f"{unit_info}{level_info} {formatted_titles}"
    
    def get_unit_title(self, target_language='en'):
        match target_language:
            case 'fr':
                return self.title_fr
            case 'es':
                return self.title_es
            case 'nl':
                return self.title_nl
            case "en":
                return self.title_en
            case _:
                return "Language not supported"
    
    @property
    def title(self):
        """Property pour compatibilité avec les templates - retourne le titre en français par défaut"""
        return self.title_fr or self.title_en
    
    @property
    def description(self):
        """Property pour compatibilité avec les templates - retourne la description en français par défaut"""
        return self.description_fr or self.description_en

    def update_unit_descriptions(self, save_immediately=True):
        """Met à jour les descriptions de l'unité pour toutes les langues"""
        languages = ['en', 'fr', 'es', 'nl']
        
        for lang in languages:
            current_desc = getattr(self, f'description_{lang}')
            new_desc = self.generate_unit_description(lang)
            
            if new_desc != current_desc:
                setattr(self, f'description_{lang}', new_desc)
        
        if save_immediately:
            Unit.objects.filter(pk=self.pk).update(
                description_en=self.description_en,
                description_fr=self.description_fr,
                description_es=self.description_es,
                description_nl=self.description_nl
            )
            self.refresh_from_db()
        
        return self

    def generate_unit_description(self, lang='en'):
        """Generate a description for the unit based on the lessons it contains."""
        default_msgs = {
            'en': f"This {self.level} unit coming soon.",
            'fr': f"Cette unité de niveau {self.level} bientôt disponible.",
            'es': f"Esta unidad de nivel {self.level} próximamente.",
            'nl': f"Deze {self.level} unit komt binnenkort."
        }
        
        if self.pk is None:
            return default_msgs.get(lang, default_msgs['en'])
        
        lessons = self.lessons.all().order_by('order')
        
        description_templates = {
            'en': "Key topics: {titles}. ({lesson_count} lessons, {duration} min)",
            'fr': "Sujets clés : {titles}. ({lesson_count} leçons, {duration} min)",
            'es': "Temas clave: {titles}. ({lesson_count} lecciones, {duration} min)",
            'nl': "Kernonderwerpen: {titles}. ({lesson_count} lessen, {duration} min)"
        }
        
        if not lessons.exists():
            return default_msgs.get(lang, default_msgs['en'])
        
        lesson_titles = [getattr(lesson, f'title_{lang}', lesson.title_en) for lesson in lessons]
        total_duration = sum(lesson.estimated_duration for lesson in lessons)
        
        max_titles = 3
        titles_display = lesson_titles[:max_titles]
        if len(lesson_titles) > max_titles:
            titles_display.append("...")
        
        return description_templates.get(lang, description_templates['en']).format(
            titles=', '.join(titles_display),
            lesson_count=len(lessons),
            duration=total_duration
        )

    def save(self, *args, update_descriptions=True, **kwargs):
        """Surcharge de save pour générer des descriptions si nécessaire"""
        if update_descriptions:
            for lang in ['en', 'fr', 'es', 'nl']:
                description = self.generate_unit_description(lang)
                setattr(self, f'description_{lang}', description)
        
        super().save(*args, **kwargs)


class Lesson(models.Model):
    """Leçon au sein d'une unité de cours."""
    
    class LessonType(models.TextChoices):
        VOCABULARY = 'vocabulary', _('Vocabulary')
        GRAMMAR = 'grammar', _('Grammar')
        CULTURE = 'culture', _('Culture')
        PROFESSIONAL = 'professional', _('Professional')

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='lessons')
    title_en = models.CharField(max_length=100, blank=False, null=False)
    title_fr = models.CharField(max_length=100, blank=False, null=False)  
    title_es = models.CharField(max_length=100, blank=False, null=False)
    title_nl = models.CharField(max_length=100, blank=False, null=False)
    description_en = models.TextField(blank=True, null=True)
    description_fr = models.TextField(blank=True, null=True)
    description_es = models.TextField(blank=True, null=True)  
    description_nl = models.TextField(blank=True, null=True)
    lesson_type = models.CharField(max_length=20, choices=LessonType.choices, default=LessonType.VOCABULARY)
    estimated_duration = models.PositiveIntegerField(default=10, help_text="Estimated duration in minutes")
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'course'
        ordering = ['unit__order', 'order']
        unique_together = [['unit', 'order']]

    def __str__(self):
        return f"Lesson {self.order}: {self.title_en} ({self.unit.title_en})"

    @property 
    def title(self):
        """Property pour compatibilité avec les templates"""
        return self.title_fr or self.title_en
    
    @property
    def description(self):
        """Property pour compatibilité avec les templates"""
        return self.description_fr or self.description_en


class ContentLesson(models.Model):
    """Contenu spécifique d'une leçon (exercices, théorie, etc.)."""
    
    CONTENT_TYPE_CHOICES = [
        ('vocabulary', 'Vocabulary'),
        ('grammar', 'Grammar'),
        ('theory', 'Theory'),
        ('multiple_choice', 'Multiple Choice'),
        ('matching', 'Matching'),
        ('fill_blank', 'Fill in the Blank'),
        ('speaking', 'Speaking'),
        ('Test Recap', 'Test Recap'),
        ('reordering', 'Reordering'),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='content_lessons')
    title_en = models.CharField(max_length=100, blank=False, null=False)
    title_fr = models.CharField(max_length=100, blank=False, null=False)
    title_es = models.CharField(max_length=100, blank=False, null=False)
    title_nl = models.CharField(max_length=100, blank=False, null=False)
    instruction_en = models.TextField(blank=True, null=True)
    instruction_fr = models.TextField(blank=True, null=True)
    instruction_es = models.TextField(blank=True, null=True)
    instruction_nl = models.TextField(blank=True, null=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    estimated_duration = models.PositiveIntegerField(default=5, help_text="Estimated duration in minutes")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        app_label = 'course'
        ordering = ['lesson__unit__order', 'lesson__order', 'order']
        unique_together = [['lesson', 'order']]

    def __str__(self):
        return f"{self.title_en} ({self.content_type}) - {self.lesson.title_en}"

    @property
    def title(self):
        """Property pour compatibilité avec les templates"""
        return self.title_fr or self.title_en
    
    @property  
    def instruction(self):
        """Property pour compatibilité avec les templates"""
        return self.instruction_fr or self.instruction_en