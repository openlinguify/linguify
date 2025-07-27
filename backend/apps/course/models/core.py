from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Unit(models.Model):
    """
    Unité de cours principale, synchronisée depuis le CMS.
    Équivalent à un cours complet.
    """
    # Champs multilingues pour titre
    title_en = models.CharField(max_length=100, blank=True, null=True)
    title_fr = models.CharField(max_length=100, blank=True, null=True)
    title_es = models.CharField(max_length=100, blank=True, null=True)
    title_nl = models.CharField(max_length=100, blank=True, null=True)
    
    # Champs multilingues pour description
    description_en = models.TextField(blank=True, null=True)
    description_fr = models.TextField(blank=True, null=True)
    description_es = models.TextField(blank=True, null=True)
    description_nl = models.TextField(blank=True, null=True)
    
    # Métadonnées du cours
    level = models.CharField(
        max_length=2, 
        choices=[
            ('A1', 'A1'), ('A2', 'A2'), ('B1', 'B1'), 
            ('B2', 'B2'), ('C1', 'C1'), ('C2', 'C2')
        ],
        default='A1'
    )
    order = models.IntegerField(default=1)
    teacher_cms_id = models.IntegerField(blank=True, null=True)
    
    # Champs de gestion
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Unité de cours"
        verbose_name_plural = "Unités de cours"
        ordering = ['level', 'order']

    def __str__(self):
        return self.title or f"Unit {self.id}"

    @property
    def title(self):
        """Retourne le titre dans la première langue disponible"""
        return (self.title_fr or self.title_en or 
                self.title_es or self.title_nl or f"Unit {self.id}")

    @property
    def description(self):
        """Retourne la description dans la première langue disponible"""
        return (self.description_fr or self.description_en or 
                self.description_es or self.description_nl or "")

    def get_estimated_duration(self):
        """Calcule la durée estimée basée sur les leçons"""
        total_duration = 0
        for lesson in self.lessons.all():
            total_duration += lesson.estimated_duration
        return total_duration

    @property
    def teacher_name(self):
        """Retourne le nom du professeur (à synchroniser avec l'app teaching)"""
        # Pour l'instant, retourner un nom par défaut
        # TODO: Lier avec l'app teaching quand elle sera prête
        if self.teacher_cms_id:
            try:
                from apps.teaching.models import Teacher
                teacher = Teacher.objects.get(cms_teacher_id=self.teacher_cms_id)
                return teacher.full_name
            except (ImportError, Teacher.DoesNotExist):
                return "Équipe Linguify"
        return "Équipe Linguify"

    @property
    def price(self):
        """Prix du cours (pour l'instant gratuit, à implémenter)"""
        return 0

    @property
    def is_free(self):
        """Si le cours est gratuit"""
        return True


class Chapter(models.Model):
    """
    Chapitre dans une unité de cours, synchronisé depuis le CMS.
    """
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='chapters')
    
    # Champs multilingues pour titre
    title_en = models.CharField(max_length=100, blank=True, null=True)
    title_fr = models.CharField(max_length=100, blank=True, null=True)
    title_es = models.CharField(max_length=100, blank=True, null=True)
    title_nl = models.CharField(max_length=100, blank=True, null=True)
    
    # Champs multilingues pour description
    description_en = models.TextField(blank=True, null=True)
    description_fr = models.TextField(blank=True, null=True)
    description_es = models.TextField(blank=True, null=True)
    description_nl = models.TextField(blank=True, null=True)
    
    # Métadonnées du chapitre
    theme = models.CharField(max_length=50, blank=True, null=True)
    order = models.IntegerField(default=1)
    style = models.CharField(
        max_length=20,
        choices=[
            ('Open Linguify', 'Open Linguify Style'),
            ('OpenLinguify', 'OpenLinguify Style'),
            ('custom', 'Custom Style')
        ],
        default='Open Linguify'
    )
    points_reward = models.IntegerField(default=100)
    
    # Champs de gestion
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chapitre"
        verbose_name_plural = "Chapitres"
        ordering = ['unit', 'order']
        unique_together = ('unit', 'order')

    def __str__(self):
        return f"{self.unit.title} - {self.title}"

    @property
    def title(self):
        """Retourne le titre dans la première langue disponible"""
        return (self.title_fr or self.title_en or 
                self.title_es or self.title_nl or f"Chapitre {self.id}")

    @property
    def description(self):
        """Retourne la description dans la première langue disponible"""
        return (self.description_fr or self.description_en or 
                self.description_es or self.description_nl or "")


class Lesson(models.Model):
    """
    Leçon individuelle, peut être dans un chapitre ou directement dans une unité.
    Synchronisée depuis le CMS.
    """
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='lessons')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons', 
                               blank=True, null=True)
    
    # Champs multilingues pour titre
    title_en = models.CharField(max_length=100, blank=True, null=True)
    title_fr = models.CharField(max_length=100, blank=True, null=True)
    title_es = models.CharField(max_length=100, blank=True, null=True)
    title_nl = models.CharField(max_length=100, blank=True, null=True)
    
    # Champs multilingues pour description
    description_en = models.TextField(blank=True, null=True)
    description_fr = models.TextField(blank=True, null=True)
    description_es = models.TextField(blank=True, null=True)
    description_nl = models.TextField(blank=True, null=True)
    
    # Métadonnées de la leçon
    lesson_type = models.CharField(
        max_length=20,
        choices=[
            ('vocabulary', 'Vocabulary'),
            ('grammar', 'Grammar'),
            ('culture', 'Culture'),
            ('professional', 'Professional')
        ],
        default='vocabulary'
    )
    estimated_duration = models.IntegerField(default=10)  # en minutes
    order = models.IntegerField(default=1)
    
    # Champs de gestion
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Leçon"
        verbose_name_plural = "Leçons"
        ordering = ['unit', 'chapter', 'order']

    def __str__(self):
        chapter_name = f" - {self.chapter.title}" if self.chapter else ""
        return f"{self.unit.title}{chapter_name} - {self.title}"

    @property
    def title(self):
        """Retourne le titre dans la première langue disponible"""
        return (self.title_fr or self.title_en or 
                self.title_es or self.title_nl or f"Leçon {self.id}")

    @property
    def description(self):
        """Retourne la description dans la première langue disponible"""
        return (self.description_fr or self.description_en or 
                self.description_es or self.description_nl or "")


class ContentLesson(models.Model):
    """
    Contenu d'une leçon - pour compatibilité avec les signaux existants.
    Peut contenir du texte, des liens vers des vidéos, audio, etc.
    """
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='content')
    
    # Contenu de la leçon
    text_content = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    audio_url = models.URLField(blank=True, null=True)
    
    # Métadonnées du contenu
    content_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('video', 'Video'),
            ('audio', 'Audio'),
            ('interactive', 'Interactive'),
            ('mixed', 'Mixed')
        ],
        default='text'
    )
    
    # Champs de gestion
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contenu de leçon"
        verbose_name_plural = "Contenus de leçons"

    def __str__(self):
        return f"Contenu: {self.lesson.title}"