from django.db import models
from django.contrib.auth import get_user_model
from .core import Unit, Chapter, Lesson

User = get_user_model()


class UserProgress(models.Model):
    """
    Progression d'un utilisateur dans une unité de cours.
    Suit l'inscription et l'avancement global dans un cours.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='user_progress')
    
    # Progression générale
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    progress_percentage = models.PositiveIntegerField(default=0)
    
    # Leçon actuelle
    current_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, 
                                     blank=True, null=True, 
                                     related_name='current_for_users')
    
    # Statistiques
    total_time_spent = models.PositiveIntegerField(default=0)  # en minutes
    lessons_completed = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Progression utilisateur"
        verbose_name_plural = "Progressions utilisateur"
        db_table = 'course_user_progress'
        unique_together = ('user', 'unit')
        indexes = [
            models.Index(fields=['user', 'last_activity']),
            models.Index(fields=['unit', 'is_completed']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.unit.title} ({self.progress_percentage}%)"

    def update_progress(self):
        """Recalcule le pourcentage de progression basé sur les leçons terminées"""
        total_lessons = self.unit.lessons.filter(is_published=True).count()
        if total_lessons == 0:
            self.progress_percentage = 0
        else:
            completed_lessons = LessonProgress.objects.filter(
                user=self.user,
                lesson__unit=self.unit,
                is_completed=True
            ).count()
            self.progress_percentage = min(100, (completed_lessons * 100) // total_lessons)
            self.lessons_completed = completed_lessons
            
            # Marquer comme terminé si toutes les leçons sont finies
            if completed_lessons >= total_lessons:
                self.is_completed = True
                if not self.completion_date:
                    from django.utils import timezone
                    self.completion_date = timezone.now()
        
        self.save()

    def get_next_lesson(self):
        """Retourne la prochaine leçon à faire"""
        completed_lesson_ids = LessonProgress.objects.filter(
            user=self.user,
            lesson__unit=self.unit,
            is_completed=True
        ).values_list('lesson_id', flat=True)
        
        next_lesson = self.unit.lessons.filter(
            is_published=True
        ).exclude(
            id__in=completed_lesson_ids
        ).order_by('order').first()
        
        return next_lesson

    @property
    def total_lessons(self):
        """Nombre total de leçons dans l'unité"""
        return self.unit.lessons.filter(is_published=True).count()


class ChapterProgress(models.Model):
    """
    Progression d'un utilisateur dans un chapitre spécifique.
    Optionnel, pour un suivi plus granulaire.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chapter_progress')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='user_progress')
    
    # Progression
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    progress_percentage = models.PositiveIntegerField(default=0)
    
    # Statistiques
    time_spent = models.PositiveIntegerField(default=0)  # en minutes
    lessons_completed = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Progression de chapitre"
        verbose_name_plural = "Progressions de chapitres"
        db_table = 'course_chapter_progress'
        unique_together = ('user', 'chapter')

    def __str__(self):
        status = "Terminé" if self.is_completed else "En cours"
        return f"{self.user.username} - {self.chapter.title} ({status})"

    def update_progress(self):
        """Recalcule le pourcentage de progression du chapitre"""
        total_lessons = self.chapter.lessons.filter(is_published=True).count()
        if total_lessons == 0:
            self.progress_percentage = 0
        else:
            completed_lessons = LessonProgress.objects.filter(
                user=self.user,
                lesson__chapter=self.chapter,
                is_completed=True
            ).count()
            self.progress_percentage = min(100, (completed_lessons * 100) // total_lessons)
            self.lessons_completed = completed_lessons
            
            # Marquer comme terminé si toutes les leçons sont finies
            if completed_lessons >= total_lessons:
                self.is_completed = True
                if not self.completed_at:
                    from django.utils import timezone
                    self.completed_at = timezone.now()
        
        self.save()


class LessonProgress(models.Model):
    """
    Progression d'un utilisateur dans une leçon spécifique.
    Suit l'état de chaque leçon individuellement.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    
    # Progression - fields matching existing table
    status = models.CharField(max_length=20, default='not_started')
    progress_percentage = models.PositiveIntegerField(default=0)
    attempts = models.PositiveIntegerField(default=0)
    best_score = models.PositiveIntegerField(blank=True, null=True)
    xp_earned = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Progression de leçon"
        verbose_name_plural = "Progressions de leçons"
        db_table = 'course_lesson_progress'
        unique_together = ('user', 'lesson')
        indexes = [
            models.Index(fields=['user', 'completed_at']),
            models.Index(fields=['lesson', 'completed_at']),
        ]

    def __str__(self):
        status = "Terminée" if self.is_completed else "En cours"
        return f"{self.user.username} - {self.lesson.title} ({status})"

    @property
    def is_completed(self):
        """Vérifie si la leçon est terminée"""
        return self.status == 'completed' or self.completed_at is not None

    def mark_completed(self):
        """Marque la leçon comme terminée"""
        if not self.completed_at:
            from django.utils import timezone
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.progress_percentage = 100
            self.save()
            
            # Mettre à jour la progression de l'unité
            try:
                unit_progress = UserProgress.objects.get(
                    user=self.user, 
                    unit=self.lesson.unit
                )
                unit_progress.update_progress()
                
                # Mettre à jour la progression du chapitre si applicable
                if self.lesson.chapter:
                    chapter_progress, created = ChapterProgress.objects.get_or_create(
                        user=self.user,
                        chapter=self.lesson.chapter
                    )
                    chapter_progress.update_progress()
                    
            except UserProgress.DoesNotExist:
                # Créer la progression de l'unité si elle n'existe pas
                UserProgress.objects.create(
                    user=self.user,
                    unit=self.lesson.unit
                ).update_progress()

    def add_xp(self, xp_points):
        """Ajoute des points d'expérience pour cette leçon"""
        self.xp_earned += xp_points
        self.save()
        
    def update_score(self, score):
        """Met à jour le meilleur score"""
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.save()