from django.db import models
from django.contrib.auth import get_user_model
from .core import Unit, Chapter, Lesson

User = get_user_model()


class UserProgress(models.Model):
    """
    Progression globale d'un utilisateur sur la plateforme.
    Suit les statistiques générales et la progression.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
    
    # Statistiques générales - matching existing table structure
    total_xp = models.PositiveIntegerField(default=0)
    streak_days = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(auto_now=True)
    current_level = models.CharField(max_length=10, default='A1')
    total_study_time = models.PositiveIntegerField(default=0)  # en minutes
    overall_progress = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Progression utilisateur"
        verbose_name_plural = "Progressions utilisateur"
        db_table = 'course_user_progress'

    def __str__(self):
        return f"{self.user.username} - {self.current_level} ({self.overall_progress}%)"

    def add_xp(self, xp_points):
        """Ajoute des points d'expérience"""
        self.total_xp += xp_points
        self.save()

    def add_study_time(self, minutes):
        """Ajoute du temps d'étude"""
        self.total_study_time += minutes
        self.save()

    def update_streak(self):
        """Met à jour la streak de jours consécutifs"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.last_activity_date == today:
            # Déjà étudié aujourd'hui
            return
        elif self.last_activity_date == today - timezone.timedelta(days=1):
            # Étudié hier, continuer la streak
            self.streak_days += 1
        else:
            # Streak cassée
            self.streak_days = 1
        
        self.last_activity_date = today
        self.save()


class UnitProgress(models.Model):
    """
    Progression d'un utilisateur dans une unité de cours spécifique.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unit_progress')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='user_progress')
    
    # Progression dans l'unité - matching existing table structure
    status = models.CharField(max_length=20, default='not_started')
    progress_percentage = models.PositiveIntegerField(default=0)
    chapters_completed = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Progression d'unité"
        verbose_name_plural = "Progressions d'unités"
        db_table = 'course_unit_progress'
        unique_together = ('user', 'unit')

    def __str__(self):
        return f"{self.user.username} - {self.unit.title} ({self.progress_percentage}%)"

    @property 
    def is_completed(self):
        """Vérifie si l'unité est terminée"""
        return self.status == 'completed' or self.completed_at is not None

    def update_progress(self):
        """Recalcule le pourcentage de progression basé sur les leçons terminées"""
        total_lessons = self.unit.lessons.count()
        if total_lessons == 0:
            self.progress_percentage = 0
        else:
            completed_lessons = LessonProgress.objects.filter(
                user=self.user,
                lesson__unit=self.unit,
                status='completed'
            ).count()
            self.progress_percentage = min(100, (completed_lessons * 100) // total_lessons)
            self.lessons_completed = completed_lessons
            
            # Marquer comme terminé si toutes les leçons sont finies
            if completed_lessons >= total_lessons:
                self.status = 'completed'
                if not self.completed_at:
                    from django.utils import timezone
                    self.completed_at = timezone.now()
        
        self.save()

    def get_next_lesson(self):
        """Retourne la prochaine leçon à faire"""
        completed_lesson_ids = LessonProgress.objects.filter(
            user=self.user,
            lesson__unit=self.unit,
            status='completed'
        ).values_list('lesson_id', flat=True)
        
        next_lesson = self.unit.lessons.exclude(
            id__in=completed_lesson_ids
        ).order_by('order').first()
        
        return next_lesson

    @property
    def total_lessons(self):
        """Nombre total de leçons dans l'unité"""
        return self.unit.lessons.count()
        
    def get_current_lesson(self):
        """Retourne la leçon actuelle ou la prochaine"""
        return self.get_next_lesson()


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
        total_lessons = self.chapter.lessons.count()
        if total_lessons == 0:
            self.progress_percentage = 0
        else:
            completed_lessons = LessonProgress.objects.filter(
                user=self.user,
                lesson__chapter=self.chapter,
                status='completed'
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
                unit_progress = UnitProgress.objects.get(
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
                    
            except UnitProgress.DoesNotExist:
                # Créer la progression de l'unité si elle n'existe pas
                UnitProgress.objects.create(
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