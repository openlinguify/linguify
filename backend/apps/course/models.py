# -*- coding: utf-8 -*-
# Part of Open Linguify. See LICENSE file for full copyright and licensing details.
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext as _
from apps.authentication.models import User
from typing import Optional
from django.core.exceptions import ValidationError
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

""" Learning Path Overview:
-----------------------
1. Languages:
    - English, French, Spanish, Dutch.
2. Levels:
    - A1 to C2.
3. Units:
    - Unit 1: Vocabulary, Theory, and Exercises.
    - Unit 2: Grammar and Exercises.
4. Progression:
    - Includes Theory -> Exercises -> Test.

Refer to the diagram for more details: path/to/image.png
"""

""" class MultilingualMixin:
    def get_localized_field(self, field_base_name, target_language='en'):
        field_name = f"{field_base_name}_{target_language}"
        return getattr(self, field_name, getattr(self, f"{field_base_name}_en", None))
"""
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

class Unit(models.Model):
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
        
        # Format spécifique pour le test, avec troncature exacte à 20 caractères
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
        """
        Met à jour les descriptions de l'unité pour toutes les langues
        """
        languages = ['en', 'fr', 'es', 'nl']
        
        for lang in languages:
            # Récupérer la description actuelle pour comparaison
            current_desc = getattr(self, f'description_{lang}')
            
            # Générer la nouvelle description
            new_desc = self.generate_unit_description(lang)
            
            # Mettre à jour seulement si différente
            if new_desc != current_desc:
                setattr(self, f'description_{lang}', new_desc)
        
        if save_immediately:
            # Force la sauvegarde avec update pour éviter le hook de save()
            Unit.objects.filter(pk=self.pk).update(
                description_en=self.description_en,
                description_fr=self.description_fr,
                description_es=self.description_es,
                description_nl=self.description_nl
            )
            
            # Recharger l'objet depuis la base de données pour être sûr
            self.refresh_from_db()
        
        return self

    def generate_unit_description(self, lang='en'):
        """
        Generate a description for the unit based on the lessons it contains.
        """
        # Messages par défaut
        default_msgs = {
            'en': f"This {self.level} unit coming soon.",
            'fr': f"Cette unité de niveau {self.level} bientôt disponible.",
            'es': f"Esta unidad de nivel {self.level} próximamente.",
            'nl': f"Deze {self.level} unit komt binnenkort."
        }
        
        # Vérifier si l'unité a déjà une clé primaire
        if self.pk is None:
            return default_msgs.get(lang, default_msgs['en'])
        
        # Une fois que l'unité a une clé primaire, on peut accéder aux leçons
        lessons = self.lessons.all().order_by('order')
        
        # Templates de description par langue
        description_templates = {
            'en': "Key topics: {titles}. ({lesson_count} lessons, {duration} min)",
            'fr': "Sujets clés : {titles}. ({lesson_count} leçons, {duration} min)",
            'es': "Temas clave: {titles}. ({lesson_count} lecciones, {duration} min)",
            'nl': "Kernonderwerpen: {titles}. ({lesson_count} lessen, {duration} min)"
        }
        
        if not lessons.exists():
            return default_msgs.get(lang, default_msgs['en'])
        
        # Récupérer les titres de leçons
        lesson_titles = [getattr(lesson, f'title_{lang}', lesson.title_en) for lesson in lessons]
        total_duration = sum(lesson.estimated_duration for lesson in lessons)
        
        # Limiter le nombre de titres
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
        """
        Surcharge de save pour générer des descriptions si nécessaire
        """
        # Générer des descriptions uniquement si update_descriptions est True
        if update_descriptions:
            for lang in ['en', 'fr', 'es', 'nl']:
                description = self.generate_unit_description(lang)
                setattr(self, f'description_{lang}', description)
        
        super().save(*args, **kwargs)

class Lesson(models.Model):
    class LessonType(models.TextChoices):
        VOCABULARY = 'vocabulary', _('Vocabulary')
        GRAMMAR = 'grammar', _('Grammar')
        CULTURE = 'culture', _('Culture')
        PROFESSIONAL = 'professional', _('Professional')
    PROFESSIONAL_CHOICES = [
        # Health and medicine
        ('medical_doctor', 'Medical Doctor'),
        ('nursing', 'Nursing'),
        ('dentistry', 'Dentistry'),
        ('pharmacy', 'Pharmacy'),
        ('physiotherapy', 'Physiotherapy'),
        ('psychology', 'Psychology'),
        ('psychiatry', 'Psychiatry'),
        ('veterinary', 'Veterinary Medicine'),
        ('optometry', 'Optometry'),
        ('radiology', 'Radiology'),
        ('surgery', 'Surgery'),
        ('public_health', 'Public Health'),
        ('nutrition', 'Nutrition'),
        
        # Droit et justice
        ('law', 'Law'),
        ('criminal_law', 'Criminal Law'),
        ('civil_law', 'Civil Law'),
        ('corporate_law', 'Corporate Law'),
        ('international_law', 'International Law'),
        ('intellectual_property', 'Intellectual Property'),
        ('legal_assistance', 'Legal Assistance'),
        ('notary', 'Notary'),
        
        # Finance et comptabilité
        ('accounting', 'Accounting'),
        ('auditing', 'Auditing'),
        ('financial_analysis', 'Financial Analysis'),
        ('banking', 'Banking'),
        ('investment', 'Investment'),
        ('insurance', 'Insurance'),
        ('tax_consulting', 'Tax Consulting'),
        ('financial_planning', 'Financial Planning'),
        
        # Affaires et gestion
        ('business_management', 'Business Management'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('human_resources', 'Human Resources'),
        ('consulting', 'Consulting'),
        ('entrepreneurship', 'Entrepreneurship'),
        ('project_management', 'Project Management'),
        ('operations_management', 'Operations Management'),
        ('supply_chain', 'Supply Chain Management'),
        
        # Immobilier et construction
        ('real_estate', 'Real Estate'),
        ('architecture', 'Architecture'),
        ('civil_engineering', 'Civil Engineering'),
        ('construction', 'Construction'),
        ('interior_design', 'Interior Design'),
        ('urban_planning', 'Urban Planning'),
        ('property_management', 'Property Management'),
        
        # Technologies et informatique
        ('software_development', 'Software Development'),
        ('web_development', 'Web Development'),
        ('data_science', 'Data Science'),
        ('cybersecurity', 'Cybersecurity'),
        ('network_administration', 'Network Administration'),
        ('database_administration', 'Database Administration'),
        ('it_support', 'IT Support'),
        ('artificial_intelligence', 'Artificial Intelligence'),
        ('cloud_computing', 'Cloud Computing'),
        
        # Ingénierie
        ('mechanical_engineering', 'Mechanical Engineering'),
        ('electrical_engineering', 'Electrical Engineering'),
        ('chemical_engineering', 'Chemical Engineering'),
        ('aerospace_engineering', 'Aerospace Engineering'),
        ('industrial_engineering', 'Industrial Engineering'),
        ('biomedical_engineering', 'Biomedical Engineering'),
        ('environmental_engineering', 'Environmental Engineering'),
        
        # Éducation
        ('teaching', 'Teaching'),
        ('university_professor', 'University Professor'),
        ('early_childhood_education', 'Early Childhood Education'),
        ('special_education', 'Special Education'),
        ('educational_administration', 'Educational Administration'),
        ('adult_education', 'Adult Education'),
        ('language_instruction', 'Language Instruction'),
        
        # Communications et média
        ('journalism', 'Journalism'),
        ('public_relations', 'Public Relations'),
        ('publishing', 'Publishing'),
        ('advertising', 'Advertising'),
        ('broadcasting', 'Broadcasting'),
        ('film_and_tv_production', 'Film and TV Production'),
        ('social_media_management', 'Social Media Management'),
        
        # Arts et design
        ('graphic_design', 'Graphic Design'),
        ('music', 'Music'),
        ('fine_arts', 'Fine Arts'),
        ('fashion_design', 'Fashion Design'),
        ('photography', 'Photography'),
        ('game_design', 'Game Design'),
        ('performing_arts', 'Performing Arts'),
        
        # Services
        ('hospitality', 'Hospitality'),
        ('culinary_arts', 'Culinary Arts'),
        ('tourism', 'Tourism'),
        ('event_planning', 'Event Planning'),
        ('beauty_and_wellness', 'Beauty and Wellness'),
        ('fitness_and_sports', 'Fitness and Sports'),
        ('customer_service', 'Customer Service'),
        
        # Transport et logistique
        ('aviation', 'Aviation'),
        ('maritime', 'Maritime'),
        ('logistics', 'Logistics'),
        ('transportation', 'Transportation'),
        ('shipping', 'Shipping'),
        ('railway', 'Railway'),
        
        # Sciences
        ('biology', 'Biology'),
        ('chemistry', 'Chemistry'),
        ('physics', 'Physics'),
        ('astronomy', 'Astronomy'),
        ('geology', 'Geology'),
        ('meteorology', 'Meteorology'),
        ('oceanography', 'Oceanography'),
        ('environmental_science', 'Environmental Science'),
        
        # Secteur public
        ('government', 'Government'),
        ('public_administration', 'Public Administration'),
        ('diplomacy', 'Diplomacy'),
        ('military', 'Military'),
        ('law_enforcement', 'Law Enforcement'),
        ('firefighting', 'Firefighting'),
        ('emergency_services', 'Emergency Services'),
        
        # Agriculture et environnement
        ('agriculture', 'Agriculture'),
        ('forestry', 'Forestry'),
        ('fishing', 'Fishing'),
        ('conservation', 'Conservation'),
        ('renewable_energy', 'Renewable Energy'),
        ('horticulture', 'Horticulture'),
        
        # Industrie
        ('manufacturing', 'Manufacturing'),
        ('automotive', 'Automotive'),
        ('textiles', 'Textiles'),
        ('food_production', 'Food Production'),
        ('petroleum', 'Petroleum'),
        ('mining', 'Mining'),
        ('pharmaceuticals', 'Pharmaceuticals'),
        
        # Social et communautaire
        ('social_work', 'Social Work'),
        ('counseling', 'Counseling'),
        ('community_development', 'Community Development'),
        ('non_profit', 'Non-Profit'),
        ('religious', 'Religious'),
        ('volunteer_management', 'Volunteer Management'),
        
        # Autres
        ('research', 'Research'),
        ('translation', 'Translation'),
        ('interpretation', 'Interpretation'),
        ('museum_and_heritage', 'Museum and Heritage'),
        ('library_science', 'Library Science'),
        ('career_counseling', 'Career Counseling'),
    ]
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='lessons')
    lesson_type = models.CharField(max_length=100, choices=LessonType.choices)
    professional_field = models.CharField(max_length=100, choices=PROFESSIONAL_CHOICES, blank=True, null=True)
    title_en = models.CharField(max_length=255, blank=False, null=False)
    title_fr = models.CharField(max_length=255, blank=False, null=False)
    title_es = models.CharField(max_length=255, blank=False, null=False)
    title_nl = models.CharField(max_length=255, blank=False, null=False)
    description_en = models.TextField(blank=True, null=True)
    description_fr = models.TextField(blank=True, null=True)
    description_es = models.TextField(blank=True, null=True)
    description_nl = models.TextField(blank=True, null=True)
    estimated_duration = models.IntegerField(default=0, help_text="In minutes", validators=[MinValueValidator(0)])
    order = models.PositiveIntegerField(blank=False, null=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        ordering = ['unit__level', 'unit__order', 'order']
        indexes = [
            models.Index(fields=['lesson_type']),
            models.Index(fields=['unit', 'order']),
            models.Index(fields=['professional_field']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['unit', 'order'], name='unique_lesson_order_per_unit')
        ]

    def __str__(self):
        return f"{self.unit} - {self.unit.title_en} - {self.title_en} - {self.lesson_type}"

    def get_title(self, target_language: str = 'en') -> str:
        """Récupère le titre dans la langue spécifiée avec une approche cohérente"""
        return getattr(self, f'title_{target_language}', self.title_en)
    
    def get_description(self, target_language: str) -> str | None:
        """Récupère la description dans la langue spécifiée"""
        return getattr(self, f'description_{target_language}', self.description_en)
    
    @property
    def title(self):
        """Property pour compatibilité avec les templates - retourne le titre en français par défaut"""
        return self.title_fr or self.title_en
    
    @property
    def description(self):
        """Property pour compatibilité avec les templates - retourne la description en français par défaut"""
        return self.description_fr or self.description_en
    
    def calculate_duration_lesson(self):
        """
        Calculate the total estimated duration of all content lessons associated with this lesson.
        
        Returns:
            int: Total estimated duration in minutes
        """
        total_duration = self.content_lessons.aggregate(
            total_duration=models.Sum('estimated_duration')
        )['total_duration'] or 0
        
        return total_duration

    def clean(self):
        if self.lesson_type == 'professional' and not self.professional_field:
            raise ValidationError({'professional_field': _('This field is required when lesson type is professional.')})
        if self.lesson_type != 'professional' and self.professional_field:
            self.professional_field = None
        
    def save(self, *args, **kwargs):
        if self.pk:
            total_duration = self.calculate_duration_lesson()
            self.estimated_duration = max(int(total_duration or 0), 0)
        super().save(*args, **kwargs)
        if not self.pk:
            self.estimated_duration = 0
    
class ContentLesson(models.Model):
    '''
    Content lesson model
    This is the area where the content of the lesson is stored.
    While you have created a lesson, you can add content to it.
    For instance, you can add a theory, vocabulary, grammar, etc. ==> titre= "Vocabulaire, Théorie, Un point de Grammaire, etc."    
    '''

    CONTENT_TYPE = [
        ('Theory', 'Theory'),
        ('VocabularyList', 'VocabularyList'),
        ('Grammar', 'Grammar'),
        ('Multiple choice', 'Multiple choice'),
        ('Numbers', 'Numbers'),
        ('Reordering', 'Reordering'),
        ('Matching', 'Matching'),
        ('Speaking', 'Speaking'),
        ('Question and answer', 'Question and answer'),
        ('fill_blank', 'Fill in the blanks'),
        ('True or False', 'True or False'),
        ('Test', 'Test'),
        ('test_recap', 'Test Recap'),
    ]
        
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='content_lessons')
    content_type = models.CharField(max_length=100, choices=CONTENT_TYPE, blank=False, null=False, db_index=True)
    title_en = models.CharField(max_length=255, blank=False, null=False)
    title_fr = models.CharField(max_length=255, blank=False, null=False)
    title_es = models.CharField(max_length=255, blank=False, null=False)
    title_nl = models.CharField(max_length=255, blank=False, null=False)
    instruction_en = models.TextField(blank=False, null=False, default='Text of the instruction')
    instruction_fr = models.TextField(blank=False, null=False, default='Text of the instruction')
    instruction_es = models.TextField(blank=False, null=False, default='Text of the instruction')
    instruction_nl = models.TextField(blank=False, null=False, default='Text of the instruction')
    estimated_duration = models.IntegerField(help_text="Duration in minutes", validators=[MinValueValidator(1)], blank=False, null=False)
    order = models.PositiveIntegerField(blank=False, validators=[MinValueValidator(1)],null=False, default=1)

    class Meta:
        ordering = ['order', 'id']
        verbose_name= "Content Lesson"
        verbose_name_plural = "Content Lessons"
        indexes = [
            models.Index(fields=['content_type']),
            models.Index(fields=['order']),
        ]


    def __str__(self):
        return f"{self.lesson.title_en} - {self.title_en} - {self.content_type} - {self.order}"
    
    def get_title(self, target_language='en'):
        """
        Get the title in the specified language.
        
        Args:
            target_language (str): Language code ('en', 'fr', 'es', or 'nl')
            
        Returns:
            str: Title in the requested language
        """
        return getattr(self, f'title_{target_language}', self.title_en)

    def get_instruction(self, target_language='en'):
        """
        Get the instruction in the specified language.
        
        Args:
            target_language (str): Language code ('en', 'fr', 'es', or 'nl')
            
        Returns:
            str: Instruction in the requested language
        """
        return getattr(self, f'instruction_{target_language}', self.instruction_en)

  
    def save(self, *args, **kwargs):
        """Override save to validate duration"""
        if self.estimated_duration is None or self.estimated_duration < 1:
            self.estimated_duration = 1
        super().save(*args, **kwargs)

''' This section if for the content of the lesson of Linguify
    The content of the lesson can be a theory, vocabulary, grammar, multiple choice, numbers, reordering, matching, question and answer, fill in the blanks, true or false, test, etc.
    The content of the lesson is stored in the ContentLesson model.
    The content of the lesson can be in different languages: English, French, Spanish, Dutch.
'''
  
class VocabularyList(models.Model):
    id = models.AutoField(primary_key=True)
    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='vocabulary_lists', default=1)
    word_en = models.CharField(max_length=100, blank=False, null=False)
    word_fr = models.CharField(max_length=100, blank=False, null=False)
    word_es = models.CharField(max_length=100, blank=False, null=False)
    word_nl = models.CharField(max_length=100, blank=False, null=False)
    definition_en = models.TextField(blank=False, null=False)
    definition_fr = models.TextField(blank=False, null=False)
    definition_es = models.TextField(blank=False, null=False)
    definition_nl = models.TextField(blank=False, null=False)
    example_sentence_en = models.TextField(blank=True, null=True)
    example_sentence_fr = models.TextField(blank=True, null=True)
    example_sentence_es = models.TextField(blank=True, null=True)
    example_sentence_nl = models.TextField(blank=True, null=True)
    word_type_en = models.CharField(max_length=100, blank=False, null=False)
    word_type_fr = models.CharField(max_length=100, blank=False, null=False)
    word_type_es = models.CharField(max_length=100, blank=False, null=False)
    word_type_nl = models.CharField(max_length=100, blank=False, null=False)
    synonymous_en = models.TextField(blank=True, null=True)
    synonymous_fr = models.TextField(blank=True, null=True)
    synonymous_es = models.TextField(blank=True, null=True)
    synonymous_nl = models.TextField(blank=True, null=True)
    antonymous_en = models.TextField(blank=True, null=True)
    antonymous_fr = models.TextField(blank=True, null=True)
    antonymous_es = models.TextField(blank=True, null=True)
    antonymous_nl = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.id} - {self.content_lesson} - {self.word_en} - {self.definition_en}"

    def get_translation(self, target_language):
        switch = {
            'fr': self.word_fr,
            'es': self.word_es,
            'nl': self.word_nl,
        }
        return switch.get(target_language, self.word_en)

    def get_example_sentence(self, target_language):
        switch = {
            'fr': self.example_sentence_fr,
            'es': self.example_sentence_es,
            'nl': self.example_sentence_nl,
        }
        return switch.get(target_language, self.example_sentence_en)

    def get_definition(self, target_language):
        switch = {
            'fr': self.definition_fr,
            'es': self.definition_es,
            'nl': self.definition_nl,
        }
        return switch.get(target_language, self.definition_en)
    
    def get_word_type(self, target_language):
        switch = {
            'fr': self.word_type_fr,
            'es': self.word_type_es,
            'nl': self.word_type_nl,
        }
        return switch.get(target_language, self.word_type_en)
    
    def get_synonymous(self, target_language):
        switch = {
            'fr': self.synonymous_fr,
            'es': self.synonymous_es,
            'nl': self.synonymous_nl,
        }
        return switch.get(target_language, self.synonymous_en)
    
    def get_antonymous(self, target_language):
        switch = {
            'fr': self.antonymous_fr,
            'es': self.antonymous_es,
            'nl': self.antonymous_nl,
        }
        return switch.get(target_language, self.antonymous_en)
    
    # Nouvelles méthodes pour l'association avec les exercices de matching
    def associate_with_matching_exercise(self, exercise):
        """
        Associe ce mot de vocabulaire avec un exercice de matching spécifié.
        
        Args:
            exercise: Instance de MatchingExercise avec laquelle associer ce mot
        
        Returns:
            bool: True si l'association a réussi, False sinon
        """
        if not exercise.id:
            return False
        
        exercise.vocabulary_words.add(self)
        return True
    
    @classmethod
    def associate_batch_with_matching(cls, vocabulary_items, exercise):
        """
        Associe un lot de mots de vocabulaire avec un exercice de matching.
        
        Args:
            vocabulary_items: QuerySet ou liste d'instances VocabularyList
            exercise: Instance de MatchingExercise cible
            
        Returns:
            int: Nombre de mots effectivement associés
        """
        if not exercise.id:
            return 0
        
        # Limiter au nombre de paires configuré dans l'exercice si nécessaire
        if hasattr(vocabulary_items, 'count') and vocabulary_items.count() > exercise.pairs_count:
            vocabulary_items = vocabulary_items[:exercise.pairs_count]
        elif len(vocabulary_items) > exercise.pairs_count:
            vocabulary_items = vocabulary_items[:exercise.pairs_count]
        
        # Mémoriser le compte initial
        initial_count = exercise.vocabulary_words.count()
        
        # Ajouter tous les éléments de vocabulaire
        exercise.vocabulary_words.add(*vocabulary_items)
        
        # Retourner le nombre d'éléments ajoutés
        return exercise.vocabulary_words.count() - initial_count
    
    @classmethod
    def find_vocabulary_for_matching(cls, content_lesson=None, parent_lesson=None, limit=None):
        """
        Recherche le vocabulaire disponible pour un exercice de matching.
        Recherche d'abord dans la leçon de contenu spécifiée, puis dans le parent.
        
        Args:
            content_lesson: Leçon de contenu spécifique (optionnel)
            parent_lesson: Leçon parente (optionnel)
            limit: Nombre maximum d'éléments à retourner (optionnel)
            
        Returns:
            QuerySet: Vocabulaire trouvé
        """
        if content_lesson:
            # D'abord chercher dans la leçon de contenu spécifiée
            vocab_items = cls.objects.filter(content_lesson=content_lesson)
            if vocab_items.exists():
                return vocab_items[:limit] if limit else vocab_items
        
        if parent_lesson:
            # Ensuite chercher dans toutes les leçons de type vocabulaire du parent
            vocab_lessons = ContentLesson.objects.filter(
                lesson=parent_lesson,
                content_type__icontains='vocabularylist'  # Changé pour correspondre au format de content_type
            ).order_by('order')  # Ajouter l'ordre pour prioriser les premières leçons
            
            all_vocab = cls.objects.none()
            for vocab_lesson in vocab_lessons:
                lesson_vocab = cls.objects.filter(content_lesson=vocab_lesson)
                all_vocab = all_vocab | lesson_vocab
            
            if all_vocab.exists():
                # Ordonner aléatoirement pour varier les exercices
                all_vocab = all_vocab.order_by('?')
                return all_vocab[:limit] if limit else all_vocab
        
        # Par défaut, retourner un QuerySet vide
        return cls.objects.none()
    
class MultipleChoiceQuestion(models.Model):
    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='multiple_choices', default=1)
    # example of question Level A1: What is the capital of Belgium?
    question_en = models.CharField(max_length=255, blank=False, null=False)
    question_fr = models.CharField(max_length=255, blank=False, null=False)
    question_es = models.CharField(max_length=255, blank=False, null=False)
    question_nl = models.CharField(max_length=255, blank=False, null=False)
    # example of correct answer Level A1: Brussels
    correct_answer_en = models.CharField(max_length=255, blank=False, null=False)

    fake_answer1_en = models.CharField(max_length=255, blank=False, null=False)
    fake_answer2_en = models.CharField(max_length=255, blank=False, null=False)
    fake_answer3_en = models.CharField(max_length=255, blank=False, null=False)
    fake_answer4_en = models.CharField(max_length=255, blank=False, null=False)

    hint_answer_en = models.CharField(max_length=255, blank=True, null=True)
    # example of correct answer Level A1: Bruxelles
    correct_answer_fr = models.CharField(max_length=255, blank=False, null=False)

    fake_answer1_fr = models.CharField(max_length=255, blank=False, null=False)
    fake_answer2_fr = models.CharField(max_length=255, blank=False, null=False)
    fake_answer3_fr = models.CharField(max_length=255, blank=False, null=False)
    fake_answer4_fr = models.CharField(max_length=255, blank=False, null=False)

    hint_answer_fr = models.CharField(max_length=255, blank=True, null=True)
    # example of correct answer Level A1: Bruselas
    correct_answer_es = models.CharField(max_length=255, blank=False, null=False)

    fake_answer1_es = models.CharField(max_length=255, blank=False, null=False)
    fake_answer2_es = models.CharField(max_length=255, blank=False, null=False)
    fake_answer3_es = models.CharField(max_length=255, blank=False, null=False)
    fake_answer4_es = models.CharField(max_length=255, blank=False, null=False)

    hint_answer_es = models.CharField(max_length=255, blank=True, null=True)

    # example of correct answer Level A1: Brussel
    correct_answer_nl = models.CharField(max_length=255, blank=False, null=False)

    fake_answer1_nl = models.CharField(max_length=255, blank=False, null=False)
    fake_answer2_nl = models.CharField(max_length=255, blank=False, null=False)
    fake_answer3_nl = models.CharField(max_length=255, blank=False, null=False)
    fake_answer4_nl = models.CharField(max_length=255, blank=False, null=False)

    hint_answer_nl = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.content_lesson} - {self.question_en}"
    
class Numbers(models.Model):
    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='numbers', default=1)
    number = models.CharField(max_length=255, blank=False, null=False)
    number_en = models.CharField(max_length=255, blank=False, null=False)
    number_fr = models.CharField(max_length=255, blank=False, null=False)
    number_es = models.CharField(max_length=255, blank=False, null=False)
    number_nl = models.CharField(max_length=255, blank=False, null=False)
    is_reviewed = models.BooleanField(default=False, blank=False, null=False)

    def __str__(self):
        return f"{self.content_lesson} - {self.content_lesson.title_en} - {self.number} - {self.number_en} - {self.is_reviewed}"  

class ExerciseVocabularyMultipleChoice(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question = models.TextField(blank=False, null=False, help_text="Question based on example sentence")
    correct_answer = models.CharField(max_length=255, blank=False, null=False, help_text="Correct answer from vocabulary")
    incorrect_answers = models.JSONField(blank=False, null=False, help_text="List of incorrect answers")
    explanation = models.TextField(blank=True, null=True, help_text="Explanation for the correct answer")

    def __str__(self):
        return f"{self.lesson.title_en} - {self.question}"
    
    @classmethod
    def create_from_vocabulary(cls, lesson, vocab):
        return cls(
            lesson=lesson,
            question=vocab.example_sentence_en,
            correct_answer=vocab.word_en,
            incorrect_answers=[vocab.word_fr, vocab.word_es, vocab.word_nl],
            explanation=f"{vocab.word_en} means {vocab.definition_en}",
        )

class MatchingExercise(models.Model):
    """
    Modèle pour les exercices d'association entre mots en langue cible et langue native.
    
    Les instructions sont standardisées et calculées dynamiquement pour toutes les instances,
    indépendamment de leur identifiant. Cela assure une expérience utilisateur cohérente
    tout en réduisant la complexité de gestion des données.
    """
    # Utilisation d'un AutoField explicite pour garantir que Django gère correctement la séquence
    id = models.AutoField(primary_key=True)
    
    # Relation avec la leçon
    content_lesson = models.ForeignKey(
        ContentLesson, 
        on_delete=models.CASCADE, 
        related_name='matching_exercises',
        verbose_name="Leçon associée"
    )
    
    # Paramètres de configuration
    difficulty = models.CharField(
        max_length=10, 
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default='medium',
        verbose_name="Difficulté",
        help_text="Niveau de difficulté de l'exercice"
    )
    
    order = models.PositiveIntegerField(
        default=1, 
        validators=[MinValueValidator(1)],
        verbose_name="Ordre",
        help_text="Position de l'exercice dans la séquence de leçon"
    )
    
    # Titres personnalisables (contrairement aux instructions qui sont standardisées)
    title_en = models.CharField(
        max_length=255, 
        default="Match words with their translations",
        verbose_name="Titre (EN)"
    )
    
    title_fr = models.CharField(
        max_length=255, 
        default="Associez les mots à leurs traductions",
        verbose_name="Titre (FR)"
    )
    
    title_es = models.CharField(
        max_length=255, 
        default="Relaciona las palabras con sus traducciones",
        verbose_name="Titre (ES)"
    )
    
    title_nl = models.CharField(
        max_length=255, 
        default="Koppel woorden aan hun vertalingen",
        verbose_name="Titre (NL)"
    )
    
    # Configuration de l'exercice
    vocabulary_words = models.ManyToManyField(
        VocabularyList, 
        related_name='used_in_matching_exercises',
        verbose_name="Mots de vocabulaire",
        help_text="Sélectionnez les mots à inclure dans cet exercice"
    )
    
    pairs_count = models.PositiveIntegerField(
        default=8,
        validators=[MinValueValidator(4), MaxValueValidator(20)],
        verbose_name="Nombre de paires",
        help_text="Nombre maximal de paires mot-traduction à afficher"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        ordering = ['content_lesson', 'order']
        verbose_name = "Matching Exercise"
        verbose_name_plural = "Matching Exercises"
        indexes = [
            models.Index(fields=['content_lesson', 'order']),
            models.Index(fields=['difficulty']),
        ]
    
    def __str__(self):
        return f"Association - {self.content_lesson.title_en} ({self.order})"
    
    # Instructions standardisées sous forme de propriétés calculées
    @property
    def instruction_en(self):
        return "Match each word in the language you're learning with its translation in your native language. Drag the items to create pairs."
    
    @property
    def instruction_fr(self):
        return "Associez chaque mot dans la langue que vous apprenez avec sa traduction dans votre langue maternelle. Faites glisser les éléments pour créer des paires."
    
    @property
    def instruction_es(self):
        return "Relaciona cada palabra en el idioma que estás aprendiendo con su traducción en tu idioma nativo. Arrastra los elementos para crear pares."
    
    @property
    def instruction_nl(self):
        return "Koppel elk woord in de taal die je leert aan de vertaling in je moedertaal. Sleep de items om paren te maken."
    
    def get_title(self, language_code='en'):
        field_name = f'title_{language_code}'
        return getattr(self, field_name, self.title_en)
    
    def get_instruction(self, language_code='en'):
        property_name = f'instruction_{language_code}'
        if hasattr(self, property_name):
            return getattr(self, property_name)
        return self.instruction_en  # Fallback sur l'anglais
    
    def get_matching_pairs(self, native_language='en', target_language='fr'):
        """
        Génère les paires de mots à associer entre la langue cible et la langue native.
        Version améliorée avec meilleure gestion des erreurs et valeurs par défaut.
        
        Args:
            native_language (str): Code de la langue maternelle de l'utilisateur
            target_language (str): Code de la langue que l'utilisateur apprend
            
        Returns:
            tuple: (target_words, native_words, correct_pairs)
                - target_words: Liste des mots dans la langue cible
                - native_words: Liste des mots dans la langue native (mélangés)
                - correct_pairs: Dictionnaire de correspondance {target_word: native_word}
        """
        import random
        import logging
        logger = logging.getLogger(__name__)
        
        # Vérifier que les langues sont valides
        supported_languages = ['en', 'fr', 'es', 'nl']
        if native_language not in supported_languages:
            logger.warning(f"Unsupported native language: {native_language}, falling back to 'en'")
            native_language = 'en'
        if target_language not in supported_languages:
            logger.warning(f"Unsupported target language: {target_language}, falling back to 'fr'")
            target_language = 'fr'
        
        # Éviter que les deux langues soient identiques
        if native_language == target_language:
            logger.warning(f"Native and target languages are the same ({native_language}), using 'fr' as target language")
            if native_language == 'fr':
                target_language = 'en'
            else:
                target_language = 'fr'
        
        # Obtenir les mots de vocabulaire pour l'exercice
        vocabulary_items = self.vocabulary_words.all()
        
        # Vérifier qu'il y a des mots de vocabulaire associés
        if not vocabulary_items.exists():
            logger.error(f"No vocabulary words associated with matching exercise ID: {self.id}")
            # Renvoyer des listes vides plutôt que de planter
            return [], [], {}
        
        # Si le nombre d'éléments dépasse pairs_count, sélectionner aléatoirement
        vocab_count = vocabulary_items.count()
        if vocab_count > self.pairs_count:
            try:
                # Convertir en liste pour pouvoir utiliser random.sample
                vocabulary_items = list(vocabulary_items)
                vocabulary_items = random.sample(vocabulary_items, self.pairs_count)
            except Exception as e:
                logger.error(f"Error sampling vocabulary items: {str(e)}")
                # Prendre les premiers elements comme fallback
                vocabulary_items = list(vocabulary_items)[:self.pairs_count]
        
        # Générer les paires de mots
        target_words = []
        native_words = []
        correct_pairs = {}
        
        # Log pour debugging
        logger.debug(f"Processing {len(vocabulary_items)} vocabulary items for matching exercise")
        
        # Collecter toutes les paires valides
        for vocab in vocabulary_items:
            try:
                # Récupérer le mot dans la langue cible
                target_field = f'word_{target_language}'
                target_word = getattr(vocab, target_field, None)
                
                # Récupérer le mot dans la langue native
                native_field = f'word_{native_language}'
                native_word = getattr(vocab, native_field, None)
                
                # Log pour debugging
                logger.debug(f"Processing vocab ID {vocab.id}: target ({target_field})='{target_word}', native ({native_field})='{native_word}'")
                
                # Vérifier que les deux valeurs sont disponibles
                if target_word and native_word:
                    # Éviter les doublons (en cas de mots identiques dans différentes langues)
                    if target_word not in target_words and native_word not in native_words:
                        target_words.append(target_word)
                        native_words.append(native_word)
                        correct_pairs[target_word] = native_word
                else:
                    logger.warning(f"Missing translation for vocab ID {vocab.id}: target='{target_word}', native='{native_word}'")
            except Exception as e:
                logger.error(f"Error processing vocabulary item {vocab.id}: {str(e)}")
                # Continuer avec le prochain item plutôt que de planter
                continue
        
        # Vérifier qu'on a au moins une paire
        if not target_words:
            logger.error(f"No valid word pairs found for languages: {native_language} (native) and {target_language} (target)")
            return [], [], {}
        
        # Mélanger la liste des mots natifs pour l'exercice
        shuffled_native_words = native_words.copy()
        random.shuffle(shuffled_native_words)
        
        return target_words, shuffled_native_words, correct_pairs
    
    def get_exercise_data(self, native_language='en', target_language='fr'):
        """
        Prépare toutes les données formatées nécessaires pour l'exercice.
        
        Args:
            native_language (str): Code de la langue maternelle de l'utilisateur
            target_language (str): Code de la langue que l'utilisateur apprend
            
        Returns:
            dict: Données formatées pour l'API
        """
        # Récupérer les paires de mots
        target_words, shuffled_native_words, correct_pairs = self.get_matching_pairs(
            native_language, target_language
        )
        
        # Construire la réponse complète
        return {
            'id': self.id,
            'title': self.get_title(native_language),
            'instruction': self.get_instruction(native_language),
            'difficulty': self.difficulty,
            'target_language': target_language,
            'native_language': native_language,
            'target_language_name': self._get_language_name(target_language),
            'native_language_name': self._get_language_name(native_language),
            'target_words': target_words,
            'native_words': shuffled_native_words,
            'correct_pairs': correct_pairs,
            'total_pairs': len(target_words)
        }
    
    def _get_language_name(self, language_code):
        """
        Traduit un code de langue en nom complet.
        
        Args:
            language_code (str): Code de langue ('en', 'fr', 'es', 'nl')
            
        Returns:
            str: Nom complet de la langue
        """
        language_names = {
            'en': 'English',
            'fr': 'French',
            'es': 'Spanish',
            'nl': 'Dutch'
        }
        return language_names.get(language_code, 'Unknown')
    
    @classmethod
    def create_from_content_lesson(cls, content_lesson, vocabulary_ids=None, pairs_count=8):
        """
        Crée un nouvel exercice d'association à partir d'une leçon et de mots de vocabulaire.
        
        Args:
            content_lesson: L'instance ContentLesson à associer
            vocabulary_ids: Liste des IDs de vocabulaire à inclure (optionnel)
            pairs_count: Nombre maximal de paires à inclure
            
        Returns:
            MatchingExercise: L'instance nouvellement créée
        """
        # Déterminer l'ordre du nouvel exercice
        order = cls.objects.filter(content_lesson=content_lesson).count() + 1
        
        # Créer l'exercice
        exercise = cls.objects.create(
            content_lesson=content_lesson,
            title_en=f"Matching Exercise - {content_lesson.title_en}",
            title_fr=f"Exercice d'association - {content_lesson.title_fr}",
            title_es=f"Ejercicio de correspondencia - {content_lesson.title_es}",
            title_nl=f"Matching oefening - {content_lesson.title_nl}",
            pairs_count=pairs_count,
            difficulty='medium',  # Valeur par défaut
            order=order
        )
        
        # Ajouter le vocabulaire à l'exercice
        if vocabulary_ids:
            vocabulary_items = VocabularyList.objects.filter(id__in=vocabulary_ids)
        else:
            vocabulary_items = VocabularyList.objects.filter(content_lesson=content_lesson)
        
        # Limiter au nombre spécifié
        for vocab in vocabulary_items[:pairs_count]:
            exercise.vocabulary_words.add(vocab)
        
        return exercise
    
    # Nouvelles méthodes pour faciliter la synchronisation
    def clear_vocabulary(self):
        """
        Supprime toutes les associations de vocabulaire existantes.
        
        Returns:
            int: Le nombre d'éléments qui ont été supprimés
        """
        count = self.vocabulary_words.count()
        self.vocabulary_words.clear()
        return count
    
    def auto_associate_vocabulary(self, force_update=False):
        """
        Associe automatiquement le vocabulaire disponible à cet exercice.
        
        Args:
            force_update (bool): Si True, supprime les associations existantes avant d'ajouter les nouvelles
            
        Returns:
            int: Le nombre de mots de vocabulaire associés
        """
        # Vérifier s'il y a déjà des associations
        initial_count = self.vocabulary_words.count()
        
        # Si des associations existent et force_update est False, ne rien faire
        if initial_count > 0 and not force_update:
            return 0
        
        # Supprimer les associations existantes si force_update est True
        if initial_count > 0 and force_update:
            self.vocabulary_words.clear()
        
        # Récupérer le vocabulaire disponible
        parent_lesson = self.content_lesson.lesson if self.content_lesson else None
        vocabulary_items = VocabularyList.find_vocabulary_for_matching(
            content_lesson=self.content_lesson,
            parent_lesson=parent_lesson,
            limit=self.pairs_count
        )
        
        # Vérifier si on a trouvé du vocabulaire
        if not vocabulary_items.exists():
            return 0
        
        # Ajouter le vocabulaire trouvé
        for vocab in vocabulary_items:
            self.vocabulary_words.add(vocab)
        
        # Retourner le nombre d'éléments ajoutés
        return self.vocabulary_words.count() - (0 if force_update else initial_count)
    
    @classmethod
    def auto_associate_all(cls, content_lesson_id=None, force_update=False):
        """
        Associe automatiquement le vocabulaire à tous les exercices de matching ou à ceux d'une leçon spécifique.
        
        Args:
            content_lesson_id (int): ID d'une leçon spécifique à traiter (optionnel)
            force_update (bool): Si True, remplace les associations existantes
            
        Returns:
            tuple: (exercises_count, exercises_updated, words_added) - Statistiques sur l'opération
        """
        # Préparer la requête pour sélectionner les exercices
        query = cls.objects
        if content_lesson_id:
            query = query.filter(content_lesson_id=content_lesson_id)
            
        exercises = query.all()
        exercises_count = exercises.count()
        
        # Variables pour les statistiques
        exercises_updated = 0
        words_added = 0
        
        # Traiter chaque exercice
        for exercise in exercises:
            # Vérifier s'il a déjà des associations et si on doit les remplacer
            initial_count = exercise.vocabulary_words.count()
            
            if initial_count > 0 and not force_update:
                continue
                
            # Associer automatiquement le vocabulaire
            words_added_to_exercise = exercise.auto_associate_vocabulary(force_update)
            
            if words_added_to_exercise > 0:
                exercises_updated += 1
                words_added += words_added_to_exercise
        
        return exercises_count, exercises_updated, words_added

class SpeakingExercise(models.Model):
    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='speaking_exercises')
    vocabulary_items = models.ManyToManyField(VocabularyList, related_name='speaking_exercises', verbose_name="Vocabulary Items", help_text="Vocabulary items to practice speaking")

    class Meta:
        ordering = ['content_lesson', 'id']
        verbose_name = "Speaking Exercise"
        verbose_name_plural = "Speaking Exercises"
    
    def __str__(self):
        return f"{self.content_lesson} - Speaking Exercise"
   

''' GRAMMAR LESSON :
This section is for the content of the lessson related to the grammar of Linguify.
A lesson of grammar can contain a theory, exercises, and a test.
'''

class TheoryContent(models.Model):
    '''
    Model for grammar theory content with explanations, formulas, exceptions, and examples.
    Amélioré avec des champs JSON pour une gestion plus flexible des langues.
    '''
    content_lesson = models.OneToOneField(ContentLesson, on_delete=models.CASCADE, related_name='theory_content', default=1)
    
    content_en = models.TextField(blank=False, null=False)
    content_fr = models.TextField(blank=False, null=False)
    content_es = models.TextField(blank=False, null=False)
    content_nl = models.TextField(blank=False, null=False)
    explication_en = models.TextField(blank=False, null=False)
    explication_fr = models.TextField(blank=False, null=False)
    explication_es = models.TextField(blank=False, null=False)
    explication_nl = models.TextField(blank=False, null=False)
    formula_en = models.TextField(blank=True, null=True)
    formula_fr = models.TextField(blank=True, null=True)
    formula_es = models.TextField(blank=True, null=True)
    formula_nl = models.TextField(blank=True, null=True)
    example_en = models.TextField(blank=True, null=True)
    example_fr = models.TextField(blank=True, null=True)
    example_es = models.TextField(blank=True, null=True)
    example_nl = models.TextField(blank=True, null=True)
    exception_en = models.TextField(blank=True, null=True)
    exception_fr = models.TextField(blank=True, null=True)
    exception_es = models.TextField(blank=True, null=True)
    exception_nl = models.TextField(blank=True, null=True)

    available_languages = models.JSONField(
        default=list,
        blank=True,
        help_text="Liste des codes de langue pour lesquelles ce contenu est disponible"
    )
    
    language_specific_content = models.JSONField(
        default=dict,
        blank=True,
        help_text="Contenu spécifique à une langue qui n'existe pas dans les autres langues"
    )
    
    using_json_format = models.BooleanField(
        default=False,
        help_text="Indique si cette théorie utilise le nouveau format JSON"
    )
    
    def __str__(self):
        return f"{self.content_lesson} - Grammar Content"
    
    def get_content(self, target_language):
        """
        Récupère le contenu pour la langue cible.
        Prend en charge à la fois l'ancien et le nouveau format.
        """
        
        if self.using_json_format and target_language in self.language_specific_content:
            return self.language_specific_content.get(target_language, {}).get('content', '')
            
        switch = {
            'fr': self.content_fr,
            'es': self.content_es,
            'nl': self.content_nl,
        }
        return switch.get(target_language, self.content_en)
        
    def get_explanation(self, target_language):
        """
        Récupère l'explication pour la langue cible.
        Prend en charge à la fois l'ancien et le nouveau format.
        """
        if self.using_json_format and target_language in self.language_specific_content:
            return self.language_specific_content.get(target_language, {}).get('explanation', '')
            
        switch = {
            'fr': self.explication_fr,
            'es': self.explication_es,
            'nl': self.explication_nl,
        }
        return switch.get(target_language, self.explication_en)

    def get_formula(self, target_language):
        if self.using_json_format and target_language in self.language_specific_content:
            return self.language_specific_content.get(target_language, {}).get('formula', '')
            
        switch = {
            'fr': self.formula_fr,
            'es': self.formula_es,
            'nl': self.formula_nl,
        }
        return switch.get(target_language, self.formula_en)
    
    def get_example(self, target_language):
        if self.using_json_format and target_language in self.language_specific_content:
            return self.language_specific_content.get(target_language, {}).get('example', '')
            
        switch = {
            'fr': self.example_fr,
            'es': self.example_es,
            'nl': self.example_nl,
        }
        return switch.get(target_language, self.example_en)
    
    def get_exception(self, target_language):
        if self.using_json_format and target_language in self.language_specific_content:
            return self.language_specific_content.get(target_language, {}).get('exception', '')
            
        switch = {
            'fr': self.exception_fr,
            'es': self.exception_es,
            'nl': self.exception_nl,
        }
        return switch.get(target_language, self.exception_en)
        
    def migrate_to_json_format(self):
        """
        Convertit les données des champs traditionnels vers le format JSON
        sans perdre les données existantes.
        """
        available_langs = []
        for lang in ['en', 'fr', 'es', 'nl']:
            content_field = f'content_{lang}'
            if getattr(self, content_field):
                available_langs.append(lang)
        
        language_content = {}
        
        for lang in available_langs:
            language_content[lang] = {
                'content': getattr(self, f'content_{lang}', ''),
                'explanation': getattr(self, f'explication_{lang}', ''),
                'formula': getattr(self, f'formula_{lang}', ''),
                'example': getattr(self, f'example_{lang}', ''),
                'exception': getattr(self, f'exception_{lang}', '')
            }
        
        self.available_languages = available_langs
        self.language_specific_content = language_content
        self.using_json_format = True
        
        self.save()
        
        return True
    
    def add_language_content(self, language_code, content_data):
        """
        Ajoute ou met à jour le contenu pour une langue spécifique
        en utilisant le nouveau format JSON.
        
        Args:
            language_code (str): Code de langue (en, fr, es, nl, etc.)
            content_data (dict): Dictionnaire contenant le contenu pour cette langue
        """
        if not self.using_json_format:
            self.migrate_to_json_format()
        
        if language_code not in self.available_languages:
            self.available_languages.append(language_code)
        
        self.language_specific_content[language_code] = content_data
        
        self.save()
        
        return True

class ExerciseGrammarReordering(models.Model):
    content_lesson = models.ForeignKey(ContentLesson, on_delete=models.CASCADE, related_name='reordering', default=1)
    sentence_en = models.TextField(blank=False, null=False, help_text="Sentence to reorder")
    sentence_fr = models.TextField(blank=False, null=False, help_text="Sentence to reorder")
    sentence_es = models.TextField(blank=False, null=False, help_text="Sentence to reorder")
    sentence_nl = models.TextField(blank=False, null=False, help_text="Sentence to reorder")
    explanation = models.TextField(blank=True, null=True, help_text="Explanation for the correct order")
    hint = models.TextField(blank=True, null=True, help_text="Hint to help the user")

    def __str__(self):
        return f"{self.content_lesson} - {self.sentence_en}"

class FillBlankExercise(models.Model):
    """
    Modèle pour les exercices de type "fill in the blank" multilingues.
    L'utilisateur doit choisir la bonne option pour remplir un trou dans une phrase.
    """
    # Relation avec ContentLesson
    content_lesson = models.ForeignKey('ContentLesson', on_delete=models.CASCADE, related_name='fill_blank_exercises')
    
    # Position dans la séquence d'exercices
    order = models.PositiveIntegerField(
        default=1, 
        validators=[MinValueValidator(1)],
        help_text="Ordre d'affichage de l'exercice"
    )
    
    # Instructions multilingues
    # Format: {"en": "Select the right answer", "fr": "Sélectionnez la bonne réponse", ...}
    instructions = models.JSONField(
        default=dict,
        help_text="Instructions dans différentes langues"
    )
    
    # Phrases avec marqueur pour indiquer l'emplacement du trou
    # Format: {"en": "Paris ___ in England. It's in France.", "fr": "Paris ___ en Angleterre. C'est en France.", ...}
    sentences = models.JSONField(help_text="Phrases avec emplacement marqué pour le trou (utiliser ___ pour indiquer l'emplacement)")
    
    # Options de réponse pour chaque langue
    # Format: {"en": ["is not", "are not", "am not"], "fr": ["n'est pas", "ne sont pas", "ne suis pas"], ...}
    answer_options = models.JSONField(help_text="Options de réponse pour chaque langue")
    
    # Réponses correctes pour chaque langue
    # Format: {"en": "is not", "fr": "n'est pas", ...}
    correct_answers = models.JSONField(
        help_text="Réponse correcte pour chaque langue"
    )
    
    # Indices optionnels pour aider l'utilisateur
    # Format: {"en": "Use the singular form", "fr": "Utilisez la forme singulière", ...}
    hints = models.JSONField(
        null=True,
        blank=True,
        help_text="Indices optionnels"
    )
    
    # Explications pour la réponse correcte
    # Format: {"en": "Paris is a city, so we use 'is not'", "fr": "Paris est une ville, donc on utilise 'n'est pas'", ...}
    explanations = models.JSONField(
        null=True,
        blank=True,
        help_text="Explications pour la réponse correcte"
    )
    
    # Niveau de difficulté
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ]
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    
    # Tags pour la catégorisation
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags pour catégoriser l'exercice"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['content_lesson', 'order']
        verbose_name = "Fill in the Blank Exercise"
        verbose_name_plural = "Fill in the Blank Exercises"
        indexes = [
            models.Index(fields=['content_lesson', 'order']),
            models.Index(fields=['difficulty']),
        ]
    
    def __str__(self):
        return f"Fill in the Blank - Lesson {self.content_lesson_id} - {self.order}"
    
    def get_available_languages(self):
        """Renvoie la liste des langues disponibles pour cet exercice"""
        # Une langue est considérée disponible si elle a une phrase et des options de réponse
        return [lang for lang in self.sentences.keys() 
                if lang in self.answer_options and lang in self.correct_answers]
    
    def get_content_for_language(self, language_code='en'):
        """
        Récupère tout le contenu pour une langue spécifique
        
        Args:
            language_code (str): Code de langue (ex: 'en', 'fr')
            
        Returns:
            dict: Contenu formaté pour l'exercice dans la langue spécifiée
        """
        # Si la langue demandée n'est pas disponible, utiliser l'anglais comme fallback
        fallback = 'en'
        
        # Vérifier si la langue est disponible
        available_languages = self.get_available_languages()
        if language_code not in available_languages:
            language_code = fallback if fallback in available_languages else available_languages[0]
        
        return {
            'instruction': self.instructions.get(language_code, self.instructions.get(fallback, "Select the right answer")),
            'sentence': self.sentences.get(language_code, self.sentences.get(fallback, "")),
            'options': self.answer_options.get(language_code, self.answer_options.get(fallback, [])),
            'correct_answer': self.correct_answers.get(language_code, self.correct_answers.get(fallback, "")),
            'hint': self.hints.get(language_code, self.hints.get(fallback, "")) if self.hints else "",
            'explanation': self.explanations.get(language_code, self.explanations.get(fallback, "")) if self.explanations else ""
        }
    
    def check_answer(self, user_answer, language_code='en'):
        """
        Vérifie si la réponse de l'utilisateur est correcte
        
        Args:
            user_answer (str): Réponse fournie par l'utilisateur
            language_code (str): Code de langue
            
        Returns:
            bool: True si la réponse est correcte, False sinon
        """
        correct = self.correct_answers.get(language_code, self.correct_answers.get('en', ""))
        return user_answer.strip() == correct.strip()
    
    def format_sentence_with_blank(self, language_code='en'):
        """Renvoie la phrase avec un trou (___) visible"""
        return self.sentences.get(language_code, self.sentences.get('en', ""))
    
    def format_sentence_with_answer(self, language_code='en'):
        """Renvoie la phrase avec la réponse correcte insérée"""
        sentence = self.sentences.get(language_code, self.sentences.get('en', ""))
        answer = self.correct_answers.get(language_code, self.correct_answers.get('en', ""))
        return sentence.replace('___', answer)

"""
Models for Test Recap functionality in the Linguify course app.
Will be merged into the main models.py file after review.
"""
class TestRecap(models.Model):
    """
    Model for the test recap of the lesson.
    This test combines various exercise types from the lesson for review
    and is unlocked after all lesson content is completed.
    """
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='recap_tests', null=True)
    # Main title field for database compatibility
    title = models.CharField(max_length=255, blank=False, null=False, default="Test Recap")
    # Language-specific title fields
    title_en = models.CharField(max_length=255, blank=False, null=False, default="Test Recap")
    title_fr = models.CharField(max_length=255, blank=False, null=False, default="Récapitulatif du test")
    title_es = models.CharField(max_length=255, blank=False, null=False, default="Resumen del test")
    title_nl = models.CharField(max_length=255, blank=False, null=False, default="Test samenvatting")
    # Required field for database compatibility - legacy field
    question = models.CharField(max_length=255, blank=False, null=False, default="Test")
    description_en = models.TextField(blank=True, null=True)
    description_fr = models.TextField(blank=True, null=True)
    description_es = models.TextField(blank=True, null=True)
    description_nl = models.TextField(blank=True, null=True)
    passing_score = models.FloatField(default=0.7, blank=False, null=False,
                                     help_text="Minimum score to pass (0.0-1.0)")
    time_limit = models.PositiveIntegerField(default=600, help_text="Time limit in seconds (0 = no limit)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = "Test Recap"
        verbose_name_plural = "Test Recaps"
        ordering = ['lesson', 'id']
    def __str__(self):
      title = self.title_en or self.title or "TestRecap"
      lesson_title = self.lesson.title_en if self.lesson else "No Lesson"
      return f"{title} - {lesson_title}"
    def save(self, *args, **kwargs):
        """Override save to sync title field with title_en."""
        if self.title_en and not self.title:
            self.title = self.title_en
        elif not self.title_en and self.title:
            self.title_en = self.title
        super().save(*args, **kwargs)
    
    def get_title(self, target_language='en'):
        """Returns the title in the specified language."""
        field_name = f'title_{target_language}'
        return getattr(self, field_name, self.title_en)
    
    def get_description(self, target_language='en'):
        """Returns the description in the specified language."""
        field_name = f'description_{target_language}'
        return getattr(self, field_name, self.description_en)
    
    def total_points(self):
        """Calculate the total points available in this test."""
        return self.questions.aggregate(
            total=models.Sum('points')
        )['total'] or 0


class TestRecapQuestion(models.Model):
    """
    Model linking various exercise types to a test recap.
    Allows creation of mixed exercise tests that pull from all lesson content.
    """
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('fill_blank', 'Fill in the Blank'),
        ('matching', 'Matching'),
        ('reordering', 'Reordering'),
        ('speaking', 'Speaking'),
        ('vocabulary', 'Vocabulary'),
    ]
    
    test_recap = models.ForeignKey(TestRecap, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPE_CHOICES)
    
    # Content IDs - only one should be filled based on question_type
    multiple_choice_id = models.IntegerField(null=True, blank=True)
    fill_blank_id = models.IntegerField(null=True, blank=True)
    matching_id = models.IntegerField(null=True, blank=True)
    reordering_id = models.IntegerField(null=True, blank=True)
    speaking_id = models.IntegerField(null=True, blank=True)
    vocabulary_id = models.IntegerField(null=True, blank=True)
    
    order = models.PositiveIntegerField(default=1, help_text="Order in which this question appears in the test")
    points = models.PositiveIntegerField(default=1, help_text="Points awarded for correctly answering this question")
    
    class Meta:
        ordering = ['test_recap', 'order']
        verbose_name = "Test Recap Question"
        verbose_name_plural = "Test Recap Questions"
    
    def __str__(self):
        return f"Question {self.order} ({self.question_type}) - {self.test_recap}"
    
    def get_question_content(self):
        """Returns the actual exercise object based on question_type"""
        try:
            if self.question_type == 'multiple_choice' and self.multiple_choice_id:
                return MultipleChoiceQuestion.objects.get(id=self.multiple_choice_id)
            elif self.question_type == 'fill_blank' and self.fill_blank_id:
                return FillBlankExercise.objects.get(id=self.fill_blank_id)
            elif self.question_type == 'matching' and self.matching_id:
                return MatchingExercise.objects.get(id=self.matching_id)
            elif self.question_type == 'reordering' and self.reordering_id:
                return ExerciseGrammarReordering.objects.get(id=self.reordering_id)
            elif self.question_type == 'speaking' and self.speaking_id:
                return SpeakingExercise.objects.get(id=self.speaking_id)
            elif self.question_type == 'vocabulary' and self.vocabulary_id:
                return VocabularyList.objects.get(id=self.vocabulary_id)
            return None
        except Exception as e:
            logger.error(f"Error retrieving question content: {str(e)}")
            return None
    
    def get_question_data(self, language_code='en', force_real_data=True):
        """
        Returns formatted question data suitable for the frontend
        based on the question type
        
        Args:
            language_code: The language to use for content
            force_real_data: If True, will not return demo data even if question is missing
                            (useful when generating test recaps from real data)
        """
        question = self.get_question_content()
        # If no question is found and we're forcing real data, log warning and return empty result
        if not question:
            if force_real_data:
                logger.warning(f"Question content not found for {self.question_type} ID {self.id} and force_real_data=True")
                base_data = {
                    'id': self.id,
                    'order': self.order,
                    'points': self.points,
                    'question_type': self.question_type,
                    'error': 'Question content not found',
                }
                return base_data
            else:
                # Return demo data when not forcing real data
                base_data = {
                    'id': self.id,
                    'order': self.order,
                    'points': self.points,
                    'question_type': self.question_type,
                    'is_demo': True  # Flag to indicate this is demo data
                }
                
                # Generate demo data based on question type
                if self.question_type == 'multiple_choice':
                    return {
                        **base_data,
                        'question': f"Sample multiple choice question #{self.id} for testing",
                        'options': [
                            "Correct answer", 
                            "Wrong answer 1", 
                            "Wrong answer 2", 
                            "Wrong answer 3"
                        ],
                        'correct_answer': "Correct answer",
                    }
                elif self.question_type == 'fill_blank':
                    return {
                        **base_data,
                        'sentence': f"This is a sample _____ for testing fill in the blank questions.",
                        'options': ["sentence", "example", "text", "question"],
                        'correct_answer': "sentence",
                    }
                elif self.question_type == 'matching':
                    return {
                        **base_data,
                        'target_words': ["apple", "banana", "orange", "grape"],
                        'native_words': ["pomme", "banane", "orange", "raisin"],
                        'correct_pairs': {
                            "apple": "pomme",
                            "banana": "banane",
                            "orange": "orange",
                            "grape": "raisin",
                        },
                    }
                elif self.question_type == 'vocabulary':
                    return {
                        **base_data,
                        'word': "example",
                        'definition': "a thing characteristic of its kind or illustrating a general rule",
                        'example_sentence': "This is an example of a vocabulary question",
                        'options': ["example", "sample", "instance", "case"],
                        'correct_answer': "example",
                    }
                elif self.question_type == 'reordering':
                    return {
                        **base_data,
                        'sentence': "This is a sample sentence for testing.",
                        'words': ["This", "is", "a", "sample", "sentence", "for", "testing"],
                        'correct_order': [0, 1, 2, 3, 4, 5, 6],
                    }
                elif self.question_type == 'speaking':
                    return {
                        **base_data,
                        'prompt': "Read the following sentence aloud",
                        'target_text': "This is a sample sentence for speaking practice",
                        'difficulty': "medium",
                    }
                else:
                    return base_data
            
        # If we have a real question, continue with normal processing
            
        base_data = {
            'id': self.id,
            'order': self.order,
            'points': self.points,
            'question_type': self.question_type,
        }
        
        if self.question_type == 'multiple_choice':
            # Construct field names based on language code
            question_field = f'question_{language_code}'
            correct_answer_field = f'correct_answer_{language_code}'
            fake_answer1_field = f'fake_answer1_{language_code}'
            fake_answer2_field = f'fake_answer2_{language_code}'
            fake_answer3_field = f'fake_answer3_{language_code}'
            
            # Get values with fallback to English
            question_text = getattr(question, question_field, getattr(question, 'question_en', ''))
            correct_answer = getattr(question, correct_answer_field, getattr(question, 'correct_answer_en', ''))
            fake_answer1 = getattr(question, fake_answer1_field, getattr(question, 'fake_answer1_en', ''))
            fake_answer2 = getattr(question, fake_answer2_field, getattr(question, 'fake_answer2_en', ''))
            fake_answer3 = getattr(question, fake_answer3_field, getattr(question, 'fake_answer3_en', ''))
            
            # Combine all options and shuffle them
            import random
            options = [correct_answer, fake_answer1, fake_answer2, fake_answer3]
            random.shuffle(options)
            
            return {
                **base_data,
                'question': question_text,
                'options': options,
                'correct_answer': correct_answer,
            }
        elif self.question_type == 'fill_blank':
            # FillBlankExercise has sentences, answer_options and correct_answers as JSON fields
            try:
                sentence = question.sentences.get(language_code, question.sentences.get('en', ''))
                options = question.answer_options.get(language_code, question.answer_options.get('en', []))
                correct_answer = question.correct_answers.get(language_code, question.correct_answers.get('en', ''))
                hint = question.hints.get(language_code, '') if hasattr(question, 'hints') and question.hints else ''
                
                return {
                    **base_data,
                    'sentence': sentence,
                    'options': options,
                    'correct_answer': correct_answer,
                    'hint': hint,
                }
            except (AttributeError, KeyError) as e:
                logger.error(f"Error processing fill_blank question {self.id}: {str(e)}")
                return base_data
        elif self.question_type == 'matching':
            try:
                # Getting native and target languages for a more realistic matching exercise
                native_language = language_code  # Default to same language (fallback)
                target_language = 'fr' if language_code == 'en' else 'en'  # Basic language pairing
                
                # Use the existing method if it exists, otherwise handle manually
                if hasattr(question, 'get_exercise_data') and callable(getattr(question, 'get_exercise_data')):
                    matching_data = question.get_exercise_data(
                        native_language=native_language,
                        target_language=target_language
                    )
                    return {
                        **base_data,
                        'target_words': matching_data.get('target_words', []),
                        'native_words': matching_data.get('native_words', []),
                        'correct_pairs': matching_data.get('correct_pairs', {}),
                    }
                else:
                    # Manual processing using vocabulary_words relationship
                    vocabulary_words = question.vocabulary_words.all()[:question.pairs_count] if hasattr(question, 'vocabulary_words') else []
                    
                    target_words = []
                    native_words = []
                    correct_pairs = {}
                    
                    for vocab in vocabulary_words:
                        target_word = getattr(vocab, f'word_{target_language}', '')
                        native_word = getattr(vocab, f'word_{native_language}', '')
                        
                        if target_word and native_word:
                            target_words.append(target_word)
                            native_words.append(native_word)
                            correct_pairs[target_word] = native_word
                    
                    # Shuffle native words for the frontend
                    import random
                    shuffled_native = native_words.copy()
                    random.shuffle(shuffled_native)
                    
                    return {
                        **base_data,
                        'target_words': target_words,
                        'native_words': shuffled_native,
                        'correct_pairs': correct_pairs,
                    }
            except Exception as e:
                logger.error(f"Error processing matching question {self.id}: {str(e)}")
                return base_data
        elif self.question_type == 'reordering':
            try:
                # Get sentence in requested language
                sentence_field = f'sentence_{language_code}'
                sentence = getattr(question, sentence_field, getattr(question, 'sentence_en', ''))
                
                # Split the sentence to get words for reordering
                words = sentence.split()
                
                return {
                    **base_data,
                    'sentence': sentence, 
                    'words': words,
                    'hint': getattr(question, 'hint', ''),
                    'explanation': getattr(question, 'explanation', ''),
                }
            except Exception as e:
                logger.error(f"Error processing reordering question {self.id}: {str(e)}")
                return base_data
                
        elif self.question_type == 'speaking':
            try:
                if hasattr(question, 'vocabulary_items') and hasattr(question.vocabulary_items, 'all'):
                    vocabulary_items = question.vocabulary_items.all()[:5]  # Limit to 5 items
                    
                    return {
                        **base_data,
                        'vocabulary_items': [
                            {
                                'word': getattr(item, f'word_{language_code}', getattr(item, 'word_en', '')),
                                'definition': getattr(item, f'definition_{language_code}', getattr(item, 'definition_en', '')),
                                'example': getattr(item, f'example_sentence_{language_code}', getattr(item, 'example_sentence_en', '')),
                            }
                            for item in vocabulary_items
                        ],
                        'exercise_type': 'vocabulary_speaking',
                    }
                else:
                    # Fallback for speaking exercises without vocabulary items
                    return {
                        **base_data,
                        'prompt': f"Speaking exercise {self.id}",
                        'target_text': f"Please practice speaking in the target language",
                        'exercise_type': 'general_speaking',
                    }
            except Exception as e:
                logger.error(f"Error processing speaking question {self.id}: {str(e)}")
                return base_data
                
        elif self.question_type == 'vocabulary':
            try:
                # Get basic vocabulary fields
                word = getattr(question, f'word_{language_code}', getattr(question, 'word_en', ''))
                definition = getattr(question, f'definition_{language_code}', getattr(question, 'definition_en', ''))
                example = getattr(question, f'example_sentence_{language_code}', getattr(question, 'example_sentence_en', ''))
                
                # Get translations in other languages for context
                other_languages = ['en', 'fr', 'es', 'nl']
                other_languages.remove(language_code)
                
                translations = {}
                for lang in other_languages:
                    translations[lang] = getattr(question, f'word_{lang}', '')
                
                return {
                    **base_data,
                    'word': word,
                    'definition': definition,
                    'example': example,
                    'translations': translations,
                    'word_type': getattr(question, f'word_type_{language_code}', getattr(question, 'word_type_en', '')),
                }
            except Exception as e:
                logger.error(f"Error processing vocabulary question {self.id}: {str(e)}")
                return base_data
        
        return base_data


class TestRecapResult(models.Model):
    """
    Model to track user performance on test recaps.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test_recap = models.ForeignKey(TestRecap, on_delete=models.CASCADE, related_name='user_results')
    score = models.FloatField(help_text="Score as percentage (0-100)")
    passed = models.BooleanField(default=False)
    time_spent = models.PositiveIntegerField(help_text="Time spent in seconds")
    completed_at = models.DateTimeField(auto_now_add=True)
    
    # JSON field to store detailed results per question
    detailed_results = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Format: {question_id: {correct: bool, time_spent: seconds, answer: user's answer}}"
    )
    
    class Meta:
        ordering = ['-completed_at']
        unique_together = ['user', 'test_recap', 'completed_at']
        verbose_name = "Test Recap Result"
        verbose_name_plural = "Test Recap Results"
    
    def __str__(self):
        return f"{self.user.username} - {self.test_recap} - {self.score}%"
    
    @property
    def correct_questions(self):
        """Returns the number of correctly answered questions"""
        return sum(1 for result in self.detailed_results.values() if result.get('correct', False))
    
    @property
    def total_questions(self):
        """Returns the total number of questions answered"""
        return len(self.detailed_results)
    
    @property
    def accuracy(self):
        """Returns the accuracy as a decimal (0.0-1.0)"""
        if self.total_questions == 0:
            return 0
        return self.correct_questions / self.total_questions


def generate_test_recap(lesson):
    """
    Generate a balanced TestRecap for a lesson,
    pulling from all content lessons.
    """
    # Create TestRecap instance
    title_en = f"Recap Test: {lesson.title_en}"
    test_recap = TestRecap.objects.create(
        lesson=lesson,
        title=title_en,  # Set main title field
        title_en=title_en,
        title_fr=f"Test récapitulatif: {lesson.title_fr}",
        title_es=f"Prueba de repaso: {lesson.title_es}",
        title_nl=f"Herhalingstest: {lesson.title_nl}",
        question=title_en,  # Legacy field required by the database
        passing_score=0.7,  # 70% to pass
        time_limit=600,     # 10 minutes
    )
    
    # Collect all content by type
    content_lessons = lesson.content_lessons.all()
    
    multiple_choice_qs = MultipleChoiceQuestion.objects.filter(
        content_lesson__in=content_lessons
    )
    
    fill_blank_exercises = FillBlankExercise.objects.filter(
        content_lesson__in=content_lessons
    )
    
    matching_exercises = MatchingExercise.objects.filter(
        content_lesson__in=content_lessons
    )
    
    reordering_exercises = ExerciseGrammarReordering.objects.filter(
        content_lesson__in=content_lessons
    )
    
    speaking_exercises = SpeakingExercise.objects.filter(
        content_lesson__in=content_lessons
    )
    
    vocabulary_items = VocabularyList.objects.filter(
        content_lesson__in=content_lessons
    )
    
    # Create a balanced mix (max 10 questions)
    total_questions = 0
    question_order = 1
    
    # Add multiple choice questions (30%)
    mc_count = min(3, multiple_choice_qs.count())
    for mc in multiple_choice_qs.order_by('?')[:mc_count]:
        TestRecapQuestion.objects.create(
            test_recap=test_recap,
            question_type='multiple_choice',
            multiple_choice_id=mc.id,
            order=question_order,
            points=1
        )
        question_order += 1
        total_questions += 1
    
    # Add fill-in-the-blank exercises (20%)
    fb_count = min(2, fill_blank_exercises.count())
    for fb in fill_blank_exercises.order_by('?')[:fb_count]:
        TestRecapQuestion.objects.create(
            test_recap=test_recap,
            question_type='fill_blank',
            fill_blank_id=fb.id,
            order=question_order,
            points=2  # Slightly more difficult
        )
        question_order += 1
        total_questions += 1
    
    # Add matching exercises (20%)
    match_count = min(2, matching_exercises.count())
    for match in matching_exercises.order_by('?')[:match_count]:
        TestRecapQuestion.objects.create(
            test_recap=test_recap,
            question_type='matching',
            matching_id=match.id,
            order=question_order,
            points=2
        )
        question_order += 1
        total_questions += 1
    
    # Add reordering exercises (10%)
    reorder_count = min(1, reordering_exercises.count())
    for reorder in reordering_exercises.order_by('?')[:reorder_count]:
        TestRecapQuestion.objects.create(
            test_recap=test_recap,
            question_type='reordering',
            reordering_id=reorder.id,
            order=question_order,
            points=2
        )
        question_order += 1
        total_questions += 1
        
    # Add speaking exercises (10%)
    speaking_count = min(1, speaking_exercises.count())
    for speaking in speaking_exercises.order_by('?')[:speaking_count]:
        TestRecapQuestion.objects.create(
            test_recap=test_recap,
            question_type='speaking',
            speaking_id=speaking.id,
            order=question_order,
            points=2
        )
        question_order += 1
        total_questions += 1
        
    # Add vocabulary exercises (10%)
    vocab_count = min(1, vocabulary_items.count())
    for vocab in vocabulary_items.order_by('?')[:vocab_count]:
        TestRecapQuestion.objects.create(
            test_recap=test_recap,
            question_type='vocabulary',
            vocabulary_id=vocab.id,
            order=question_order,
            points=1
        )
        question_order += 1
        total_questions += 1
    
    return test_recap

''' Others models for the content of the lesson of Linguify
'''

class Grammar(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    example = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.title

class GrammarRulePoint(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False, null=False)
    rule = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.title

class Reading(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    text = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.title

class Writing(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    text = models.TextField(blank=False, null=False)

    def __str__(self):
        return self.title