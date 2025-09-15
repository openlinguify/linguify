from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class CourseUnit(models.Model):
    """
    Représente une unité dans un cours de langue (ex: Unité 1, Unité 2, etc.)
    """
    language = models.ForeignKey('Language', on_delete=models.CASCADE, related_name='units')
    unit_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-book')
    color = models.CharField(max_length=7, default='#10b981')  # Couleur hex
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Course Unit"
        verbose_name_plural = "Course Units"
        ordering = ['language', 'order', 'unit_number']
        unique_together = ['language', 'unit_number']

    def __str__(self):
        return f"{self.language.name} - Unité {self.unit_number}: {self.title}"

    def get_modules_count(self):
        return self.modules.count()

    def get_completed_modules_for_user(self, user):
        return self.modules.filter(
            progress_records__user=user,
            progress_records__is_completed=True
        ).count()


class CourseModule(models.Model):
    """
    Représente un module dans une unité (ex: Vocabulaire, Grammaire, etc.)
    """
    MODULE_TYPE_CHOICES = [
        ('vocabulary', 'Vocabulaire'),
        ('grammar', 'Grammaire'),
        ('listening', 'Écoute'),
        ('speaking', 'Expression orale'),
        ('reading', 'Lecture'),
        ('writing', 'Écriture'),
        ('culture', 'Culture'),
        ('review', 'Révision'),
    ]

    unit = models.ForeignKey(CourseUnit, on_delete=models.CASCADE, related_name='modules')
    module_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    module_type = models.CharField(max_length=20, choices=MODULE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    content = models.JSONField(default=dict, blank=True)  # Contenu structuré du module
    estimated_duration = models.PositiveIntegerField(default=10, help_text="Durée en minutes")
    xp_reward = models.PositiveIntegerField(default=10)
    is_locked = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Course Module"
        verbose_name_plural = "Course Modules"
        ordering = ['unit', 'order', 'module_number']
        unique_together = ['unit', 'module_number']

    def __str__(self):
        return f"{self.unit} - Module {self.module_number}: {self.title}"

    def is_available_for_user(self, user):
        """Vérifie si le module est disponible pour l'utilisateur"""
        if not self.is_locked:
            return True

        # Vérifier si les modules précédents sont complétés
        previous_modules = self.unit.modules.filter(order__lt=self.order)
        for module in previous_modules:
            if not ModuleProgress.objects.filter(
                user=user,
                module=module,
                is_completed=True
            ).exists():
                return False
        return True


class ModuleProgress(models.Model):
    """
    Suivi de la progression d'un utilisateur sur un module
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='progress_records')
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)
    attempts = models.PositiveIntegerField(default=0)
    time_spent = models.PositiveIntegerField(default=0, help_text="Temps en secondes")
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Module Progress"
        verbose_name_plural = "Module Progress Records"
        unique_together = ['user', 'module']

    def __str__(self):
        return f"{self.user.username} - {self.module.title} ({'Complété' if self.is_completed else 'En cours'})"

    def complete(self, score=None):
        """Marque le module comme complété"""
        self.is_completed = True
        self.completion_date = timezone.now()
        if score:
            self.score = score
        self.save()


class UserCourseProgress(models.Model):
    """
    Progression globale d'un utilisateur dans un cours de langue
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='language_course_progress')
    language = models.ForeignKey('Language', on_delete=models.CASCADE)
    current_unit = models.ForeignKey(CourseUnit, on_delete=models.SET_NULL, null=True, blank=True)
    current_module = models.ForeignKey(CourseModule, on_delete=models.SET_NULL, null=True, blank=True)
    total_xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    started_date = models.DateTimeField(auto_now_add=True)
    last_activity_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Course Progress"
        verbose_name_plural = "User Course Progress Records"
        unique_together = ['user', 'language']

    def __str__(self):
        return f"{self.user.username} - {self.language.name} (Niveau {self.level})"

    def get_completion_percentage(self):
        """Calcule le pourcentage de complétion du cours"""
        total_modules = CourseModule.objects.filter(unit__language=self.language).count()
        completed_modules = ModuleProgress.objects.filter(
            user=self.user,
            module__unit__language=self.language,
            is_completed=True
        ).count()

        if total_modules == 0:
            return 0
        return int((completed_modules / total_modules) * 100)