"""
Content store models following OpenEdX patterns.
Handles course content, assets, and metadata.
Includes all course models migrated from course_builder.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
import uuid

from cms.core.models import TimestampedModel, SyncableModel, MultilingualMixin
from apps.teachers.models import Teacher


class CourseAsset(SyncableModel):
    """
    Model for storing course assets (images, videos, documents).
    Based on OpenEdX asset management patterns.
    """
    
    ASSET_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'), 
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('archive', 'Archive'),
        ('other', 'Other'),
    ]
    
    # Asset identification
    asset_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # File information
    display_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    
    # File storage
    content_type = models.CharField(max_length=100)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    file_path = models.FileField(
        upload_to='course_assets/%Y/%m/',
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf', 'mp4', 'mp3', 'zip', 'ppt', 'pptx']
        )]
    )
    
    # Metadata
    thumbnail = models.ImageField(upload_to='course_assets/thumbnails/', blank=True, null=True)
    is_locked = models.BooleanField(default=False, help_text="Prevents accidental deletion")
    
    # Usage tracking
    course_id = models.CharField(max_length=255, help_text="Course identifier where asset is used")
    usage_locations = models.JSONField(default=list, help_text="List of locations where asset is referenced")
    
    # Upload information
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_assets')
    
    class Meta:
        db_table = 'contentstore_course_assets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['course_id', 'asset_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.asset_type})"
    
    @property
    def file_size_display(self):
        """Human readable file size."""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
    
    def is_image(self):
        """Check if asset is an image."""
        return self.asset_type == 'image'
    
    def is_video(self):
        """Check if asset is a video."""
        return self.asset_type == 'video'


class CourseContent(SyncableModel):
    """
    Model for storing course content blocks following OpenEdX XBlock patterns.
    """
    
    CONTENT_TYPE_CHOICES = [
        ('html', 'HTML Content'),
        ('video', 'Video Content'),
        ('problem', 'Problem/Exercise'),
        ('discussion', 'Discussion'),
        ('text', 'Text Content'),
        ('sequence', 'Sequence'),
        ('vertical', 'Vertical'),
        ('chapter', 'Chapter'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('staff_only', 'Staff Only'),
    ]
    
    # Content identification
    content_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    usage_key = models.CharField(max_length=255, unique=True, help_text="Unique identifier for content block")
    
    # Course relationship
    course_id = models.CharField(max_length=255, help_text="Course identifier")
    parent_usage_key = models.CharField(max_length=255, blank=True, help_text="Parent content block")
    
    # Content metadata
    display_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    
    # Content data
    data = models.JSONField(default=dict, help_text="Content block data and settings")
    metadata = models.JSONField(default=dict, help_text="Content block metadata")
    
    # Versioning
    version = models.PositiveIntegerField(default=1)
    is_draft = models.BooleanField(default=True)
    
    # Visibility and access
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Authoring information
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_content')
    last_modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='modified_content')
    
    class Meta:
        db_table = 'contentstore_course_content'
        ordering = ['course_id', 'usage_key']
        indexes = [
            models.Index(fields=['course_id', 'content_type']),
            models.Index(fields=['usage_key']),
            models.Index(fields=['parent_usage_key']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.content_type})"
    
    def is_published(self):
        """Check if content is published (not draft)."""
        return not self.is_draft
    
    def is_visible_now(self):
        """Check if content is visible at current time."""
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class CourseSettings(TimestampedModel):
    """
    Model for storing course-level settings and configuration.
    Based on OpenEdX course settings patterns.
    """
    
    # Course identification
    course_id = models.CharField(max_length=255, unique=True)
    
    # Basic course information
    display_name = models.CharField(max_length=255)
    short_description = models.TextField(blank=True)
    overview = models.TextField(blank=True, help_text="Detailed course description")
    
    # Course metadata
    language = models.CharField(max_length=10, default='en')
    effort = models.CharField(max_length=100, blank=True, help_text="Expected effort (e.g., '2-4 hours per week')")
    
    # Dates and scheduling
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    enrollment_start = models.DateTimeField(null=True, blank=True)
    enrollment_end = models.DateTimeField(null=True, blank=True)
    
    # Course image and branding
    course_image = models.ForeignKey(
        CourseAsset, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='course_images'
    )
    
    # Advanced settings
    advanced_settings = models.JSONField(default=dict)
    
    # Policy and grading
    grading_policy = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'contentstore_course_settings'
    
    def __str__(self):
        return f"Settings for {self.display_name}"


class ContentLibrary(SyncableModel):
    """
    Model for reusable content libraries following OpenEdX patterns.
    """
    
    # Library identification
    library_key = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Library metadata
    library_type = models.CharField(max_length=50, default='problem-bank')
    version = models.PositiveIntegerField(default=1)
    
    # Access control
    allow_public_learning = models.BooleanField(default=False)
    allow_public_read = models.BooleanField(default=False)
    
    # Library settings
    bundle_uuid = models.UUIDField(default=uuid.uuid4)
    
    class Meta:
        db_table = 'contentstore_content_libraries'
        verbose_name_plural = 'Content Libraries'
    
    def __str__(self):
        return self.display_name


# =============================================================================
# COURSE MODELS (Migrated from course_builder)
# =============================================================================

class CMSUnit(SyncableModel, MultilingualMixin):
    """CMS version of Unit model - supports all types of courses."""
    
    LEVEL_CHOICES = [
        ('beginner', 'Débutant'),
        ('intermediate', 'Intermédiaire'),
        ('advanced', 'Avancé'),
        ('expert', 'Expert'),
    ]
    
    CATEGORY_CHOICES = [
        ('popular', '🔥 Populaire'),
        ('ai_digital', '🤖 IA & Transformation Digitale'),
        ('sustainability', '🌱 Durabilité'),
        ('leadership', '👥 Leadership & Compétences Interpersonnelles'),
        ('business_management', '💼 Management & Stratégie d\'Entreprise'),
        ('data_science', '📊 Data Science & Analyse'),
        ('education', '🎓 Éducation'),
        ('finance', '💰 Finance, Investissement & Immobilier'),
        ('fintech', '🏦 Fintech & Blockchain'),
        ('healthcare', '⚕️ Santé & Bien-être'),
        ('hr_talent', '👨‍💼 RH & Gestion des Talents'),
        ('it_cybersecurity', '🔒 IT & Cybersécurité'),
        ('marketing', '📈 Marketing, Vente & Design'),
        ('politics_law', '⚖️ Politique, Économie & Droit'),
        ('project_management', '📋 Gestion de Projet & Supply Chain'),
        ('languages', '🗣️ Langues'),
        ('programming', '💻 Programmation'),
        ('engineering', '🏗️ Ingénierie'),
        ('sciences', '🔬 Sciences & Maths'),
        ('creative', '🎨 Arts & Créatif'),
        ('sports', '🏃 Sport & Fitness'),
        ('other', '📚 Autre'),
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
    
    # Course classification
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    level = models.CharField(max_length=12, choices=LEVEL_CHOICES, default='beginner')
    tags = models.JSONField(default=list, help_text="Course tags like ['Python', 'Web', 'API']")
    order = models.PositiveIntegerField(default=1)
    
    # Course metadata
    duration_hours = models.PositiveIntegerField(default=10, help_text="Estimated course duration in hours")
    prerequisites = models.TextField(blank=True, help_text="Required knowledge or courses")
    learning_objectives = models.JSONField(default=list, help_text="What students will learn")
    
    # CMS specific fields
    is_published = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Ratings and enrollment
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, help_text="Average rating")
    total_enrollments = models.PositiveIntegerField(default=0)
    
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
    """CMS version of Lesson model for all types of content."""
    
    class LessonType(models.TextChoices):
        # General types
        THEORY = 'theory', '📖 Théorie'
        PRACTICE = 'practice', '💡 Pratique'
        EXERCISE = 'exercise', '✏️ Exercice'
        PROJECT = 'project', '🚀 Projet'
        QUIZ = 'quiz', '❓ Quiz'
        VIDEO = 'video', '🎥 Vidéo'
        DISCUSSION = 'discussion', '💬 Discussion'
        
        # Language specific (legacy compatibility)
        VOCABULARY = 'vocabulary', '📝 Vocabulaire'
        GRAMMAR = 'grammar', '🔤 Grammaire'
        
        # Programming specific
        CODING = 'coding', '💻 Programmation'
        DEBUG = 'debug', '🐛 Débogage'
        
        # Other specific
        LAB = 'lab', '🧪 Laboratoire'
        CASE_STUDY = 'case_study', '📋 Étude de cas'
    
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
    """CMS version of ContentLesson model for all types of learning content."""
    
    CONTENT_TYPE_CHOICES = [
        # General content types
        ('text', '📄 Texte'),
        ('video', '🎥 Vidéo'),
        ('audio', '🎵 Audio'),
        ('image', '🖼️ Image'),
        ('document', '📎 Document'),
        ('link', '🔗 Lien externe'),
        
        # Interactive content
        ('multiple_choice', '✅ QCM'),
        ('true_false', '✔️ Vrai/Faux'),
        ('fill_blank', '✏️ Texte à trous'),
        ('matching', '🔗 Association'),
        ('ordering', '📋 Tri/Ordre'),
        ('drag_drop', '🖱️ Glisser-déposer'),
        
        # Programming specific
        ('code_editor', '💻 Éditeur de code'),
        ('code_review', '👀 Revue de code'),
        ('terminal', '⌨️ Terminal'),
        
        # Language specific (legacy)
        ('vocabulary', '📝 Vocabulaire'),
        ('grammar', '🔤 Grammaire'),
        ('speaking', '🗣️ Expression orale'),
        
        # Advanced content
        ('simulation', '🎮 Simulation'),
        ('whiteboard', '📋 Tableau blanc'),
        ('poll', '📊 Sondage'),
        ('forum', '💬 Forum'),
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


# =============================================================================
# GENERAL CONTENT MODELS (Replaces language-specific models)
# =============================================================================

class CMSContentBlock(SyncableModel):
    """Generic content block for any type of learning material."""
    
    BLOCK_TYPE_CHOICES = [
        ('text', '📄 Bloc de texte'),
        ('code', '💻 Code'),
        ('quiz', '❓ Quiz'),
        ('exercise', '✏️ Exercice'),
        ('media', '🎥 Média'),
        ('resource', '📎 Ressource'),
    ]
    
    content_lesson = models.ForeignKey(CMSContentLesson, on_delete=models.CASCADE, related_name='content_blocks')
    
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    content_data = models.JSONField(default=dict, help_text="Structured content data")
    
    order = models.PositiveIntegerField(default=1)
    is_required = models.BooleanField(default=True)
    points = models.PositiveIntegerField(default=0, help_text="Points earned for completion")
    
    class Meta:
        db_table = 'cms_content_blocks'
        ordering = ['content_lesson', 'order']
        unique_together = ['content_lesson', 'order']
    
    def __str__(self):
        return f"{self.title} ({self.get_block_type_display()})"


class CMSQuizQuestion(SyncableModel):
    """Quiz questions for interactive content."""
    
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'QCM'),
        ('true_false', 'Vrai/Faux'),
        ('fill_blank', 'Texte à trous'),
        ('short_answer', 'Réponse courte'),
        ('code', 'Code'),
    ]
    
    content_block = models.ForeignKey(CMSContentBlock, on_delete=models.CASCADE, related_name='questions')
    
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    question_text = models.TextField()
    question_data = models.JSONField(default=dict, help_text="Question options, code, etc.")
    correct_answer = models.JSONField(default=dict, help_text="Correct answer(s)")
    explanation = models.TextField(blank=True)
    
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        db_table = 'cms_quiz_questions'
        ordering = ['content_block', 'order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class CMSResource(SyncableModel):
    """Learning resources (files, links, references)."""
    
    RESOURCE_TYPE_CHOICES = [
        ('file', '📎 Fichier'),
        ('link', '🔗 Lien'),
        ('book', '📚 Livre'),
        ('video', '🎥 Vidéo externe'),
        ('tool', '🔧 Outil'),
        ('dataset', '📊 Jeu de données'),
    ]
    
    content_lesson = models.ForeignKey(CMSContentLesson, on_delete=models.CASCADE, related_name='resources')
    
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    file = models.FileField(upload_to='course_resources/', blank=True)
    
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        db_table = 'cms_resources'
        ordering = ['content_lesson', 'order']
    
    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"


# =============================================================================
# LEGACY MODELS (Keep for backward compatibility)
# =============================================================================

class CMSVocabularyList(SyncableModel, MultilingualMixin):
    """Vocabulary content for language lessons (legacy)."""
    
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
    """Individual vocabulary words (legacy)."""
    
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
    """Theory content for lessons (legacy)."""
    
    content_lesson = models.OneToOneField(CMSContentLesson, on_delete=models.CASCADE, related_name='theory')
    
    content_en = models.TextField()
    content_fr = models.TextField()
    content_es = models.TextField()
    content_nl = models.TextField()
    
    class Meta:
        db_table = 'cms_theory_content'
    
    def __str__(self):
        return f"Theory: {self.content_lesson.title}"