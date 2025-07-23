"""
Course Builder models for CMS.
Compatible with backend/apps/course/ models for synchronization.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.core.models import TimestampedModel, SyncableModel, MultilingualMixin
from apps.teachers.models import Teacher

class CMSUnit(SyncableModel, MultilingualMixin):
    """CMS version of Unit model - mirrors backend Unit."""
    
    LEVEL_CHOICES = [
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
        ('C1', 'C1'),
        ('C2', 'C2'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='units')
    
    # Multilingual fields
    title_en = models.CharField(max_length=100, blank=False, null=False)
    title_fr = models.CharField(max_length=100, blank=False, null=False)
    title_es = models.CharField(max_length=100, blank=False, null=False)
    title_nl = models.CharField(max_length=100, blank=False, null=False)
    description_en = models.TextField(null=True, blank=True)
    description_fr = models.TextField(null=True, blank=True)
    description_es = models.TextField(null=True, blank=True)
    description_nl = models.TextField(null=True, blank=True)
    
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES)
    order = models.PositiveIntegerField(default=1)
    
    # CMS specific fields
    is_published = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'cms_units'
        ordering = ['order']
        unique_together = ['teacher', 'order']
    
    def __str__(self):
        return f"{self.get_localized_field('title', 'fr')} ({self.level}) - {self.teacher.full_name}"
    
    @property
    def title(self):
        return self.get_localized_field('title', 'fr')
    
    @property
    def description(self):
        return self.get_localized_field('description', 'fr')

class CMSChapter(SyncableModel, MultilingualMixin):
    """CMS version of Chapter model."""
    
    CHAPTER_STYLE_CHOICES = [
        ('Open Linguify', 'Open Linguify Style'),
        ('OpenLinguify', 'OpenLinguify Style'),
        ('custom', 'Custom Style'),
    ]
    
    unit = models.ForeignKey(CMSUnit, on_delete=models.CASCADE, related_name='chapters')
    
    title_en = models.CharField(max_length=100, blank=False, null=False)
    title_fr = models.CharField(max_length=100, blank=False, null=False)
    title_es = models.CharField(max_length=100, blank=False, null=False)
    title_nl = models.CharField(max_length=100, blank=False, null=False)
    description_en = models.TextField(blank=True, null=True)
    description_fr = models.TextField(blank=True, null=True)
    description_es = models.TextField(blank=True, null=True)
    description_nl = models.TextField(blank=True, null=True)
    
    theme = models.CharField(max_length=50, help_text="Theme like 'Introductions', 'Describing house'")
    order = models.PositiveIntegerField(default=1)
    style = models.CharField(max_length=20, choices=CHAPTER_STYLE_CHOICES, default='Open Linguify')
    points_reward = models.PositiveIntegerField(default=100)
    
    class Meta:
        db_table = 'cms_chapters'
        ordering = ['unit__order', 'order']
        unique_together = ['unit', 'order']
    
    def __str__(self):
        return f"Chapter {self.order}: {self.get_localized_field('title', 'fr')}"
    
    @property
    def title(self):
        return self.get_localized_field('title', 'fr')

class CMSLesson(SyncableModel, MultilingualMixin):
    """CMS version of Lesson model."""
    
    class LessonType(models.TextChoices):
        VOCABULARY = 'vocabulary', 'Vocabulary'
        GRAMMAR = 'grammar', 'Grammar'
        CULTURE = 'culture', 'Culture'
        PROFESSIONAL = 'professional', 'Professional'
    
    unit = models.ForeignKey(CMSUnit, on_delete=models.CASCADE, related_name='lessons')
    chapter = models.ForeignKey(CMSChapter, on_delete=models.CASCADE, related_name='lessons', null=True, blank=True)
    
    title_en = models.CharField(max_length=100, blank=False, null=False)
    title_fr = models.CharField(max_length=100, blank=False, null=False)
    title_es = models.CharField(max_length=100, blank=False, null=False)
    title_nl = models.CharField(max_length=100, blank=False, null=False)
    description_en = models.TextField(blank=True, null=True)
    description_fr = models.TextField(blank=True, null=True)
    description_es = models.TextField(blank=True, null=True)
    description_nl = models.TextField(blank=True, null=True)
    
    lesson_type = models.CharField(max_length=20, choices=LessonType.choices, default=LessonType.VOCABULARY)
    estimated_duration = models.PositiveIntegerField(default=10, help_text="Duration in minutes")
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        db_table = 'cms_lessons'
        ordering = ['unit__order', 'order']
        unique_together = ['unit', 'order']
    
    def __str__(self):
        return f"Lesson {self.order}: {self.get_localized_field('title', 'fr')}"
    
    @property
    def title(self):
        return self.get_localized_field('title', 'fr')

class CMSContentLesson(SyncableModel, MultilingualMixin):
    """CMS version of ContentLesson model."""
    
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
    
    lesson = models.ForeignKey(CMSLesson, on_delete=models.CASCADE, related_name='content_lessons')
    
    title_en = models.CharField(max_length=100, blank=False, null=False)
    title_fr = models.CharField(max_length=100, blank=False, null=False)
    title_es = models.CharField(max_length=100, blank=False, null=False)
    title_nl = models.CharField(max_length=100, blank=False, null=False)
    instruction_en = models.TextField(blank=True, null=True)
    instruction_fr = models.TextField(blank=True, null=True)
    instruction_es = models.TextField(blank=True, null=True)
    instruction_nl = models.TextField(blank=True, null=True)
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    estimated_duration = models.PositiveIntegerField(default=5, help_text="Duration in minutes")
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        db_table = 'cms_content_lessons'
        ordering = ['lesson__unit__order', 'lesson__order', 'order']
        unique_together = ['lesson', 'order']
    
    def __str__(self):
        return f"{self.get_localized_field('title', 'fr')} ({self.content_type})"
    
    @property
    def title(self):
        return self.get_localized_field('title', 'fr')

class CMSVocabularyList(SyncableModel, MultilingualMixin):
    """Vocabulary content for lessons."""
    
    content_lesson = models.OneToOneField(CMSContentLesson, on_delete=models.CASCADE, related_name='vocabulary')
    
    title_en = models.CharField(max_length=100)
    title_fr = models.CharField(max_length=100)
    title_es = models.CharField(max_length=100)
    title_nl = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'cms_vocabulary_lists'
    
    def __str__(self):
        return f"Vocabulary: {self.get_localized_field('title', 'fr')}"

class CMSVocabularyWord(SyncableModel):
    """Individual vocabulary words."""
    
    vocabulary_list = models.ForeignKey(CMSVocabularyList, on_delete=models.CASCADE, related_name='words')
    
    word_en = models.CharField(max_length=100)
    word_fr = models.CharField(max_length=100)
    word_es = models.CharField(max_length=100)
    word_nl = models.CharField(max_length=100)
    
    pronunciation = models.CharField(max_length=200, blank=True)
    audio_file = models.FileField(upload_to='vocabulary/audio/', blank=True)
    image = models.ImageField(upload_to='vocabulary/images/', blank=True)
    
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        db_table = 'cms_vocabulary_words'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.word_fr} ({self.word_en})"

class CMSTheoryContent(SyncableModel, MultilingualMixin):
    """Theory content for lessons."""
    
    content_lesson = models.OneToOneField(CMSContentLesson, on_delete=models.CASCADE, related_name='theory')
    
    content_en = models.TextField()
    content_fr = models.TextField()
    content_es = models.TextField()
    content_nl = models.TextField()
    
    class Meta:
        db_table = 'cms_theory_content'
    
    def __str__(self):
        return f"Theory: {self.content_lesson.title}"