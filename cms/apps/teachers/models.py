"""
Teacher models for CMS.
Manages teacher profiles, qualifications, and settings.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimestampedModel, SyncableModel

class Teacher(SyncableModel):
    """Teacher profile with qualifications and settings."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        APPROVED = 'approved', 'Approuvé'
        SUSPENDED = 'suspended', 'Suspendu'
        REJECTED = 'rejected', 'Rejeté'
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Profile information
    bio_en = models.TextField(blank=True, help_text="Biography in English")
    bio_fr = models.TextField(blank=True, help_text="Biography in French")
    bio_es = models.TextField(blank=True, help_text="Biography in Spanish")
    bio_nl = models.TextField(blank=True, help_text="Biography in Dutch")
    
    profile_picture = models.ImageField(upload_to='teachers/profiles/', blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, default='Europe/Paris')
    
    # Teaching qualifications
    years_experience = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(50)])
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(10)])
    
    # Teaching preferences
    max_students_per_class = models.PositiveIntegerField(default=1)
    available_for_individual = models.BooleanField(default=True)
    available_for_group = models.BooleanField(default=False)
    
    # Payment information
    bank_account = models.CharField(max_length=34, blank=True, help_text="IBAN")
    tax_id = models.CharField(max_length=50, blank=True)
    
    # Statistics
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_courses_sold = models.PositiveIntegerField(default=0)
    total_hours_taught = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'teachers'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.status}"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def is_active(self):
        return self.status == self.Status.APPROVED
    
    def get_bio(self, language='fr'):
        """Get bio in specified language with fallback."""
        bio_field = f"bio_{language}"
        if hasattr(self, bio_field):
            bio = getattr(self, bio_field)
            if bio:
                return bio
        return self.bio_en or "Pas de biographie disponible"

class TeacherLanguage(TimestampedModel):
    """Languages taught by teacher with proficiency levels."""
    
    class Proficiency(models.TextChoices):
        NATIVE = 'native', 'Langue maternelle'
        FLUENT = 'fluent', 'Courant'
        INTERMEDIATE = 'intermediate', 'Intermédiaire'
        BASIC = 'basic', 'Débutant'
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='languages')
    language_code = models.CharField(max_length=10, help_text="Language code (en, fr, es, etc.)")
    language_name = models.CharField(max_length=100, help_text="Language name")
    proficiency = models.CharField(max_length=20, choices=Proficiency.choices)
    can_teach = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'teacher_languages'
        unique_together = ['teacher', 'language_code']
        ordering = ['language_name']
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.language_name} ({self.proficiency})"

class TeacherQualification(TimestampedModel):
    """Teacher certifications and qualifications."""
    
    class QualificationType(models.TextChoices):
        DEGREE = 'degree', 'Diplôme universitaire'
        CERTIFICATE = 'certificate', 'Certificat'
        TEACHING_LICENSE = 'teaching_license', 'Licence d\'enseignement'
        LANGUAGE_CERTIFICATE = 'language_certificate', 'Certificat de langue'
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='qualifications')
    type = models.CharField(max_length=30, choices=QualificationType.choices)
    title = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year_obtained = models.PositiveIntegerField()
    certificate_file = models.FileField(upload_to='teachers/qualifications/', blank=True)
    verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'teacher_qualifications'
        ordering = ['-year_obtained']
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.title}"

class TeacherAvailability(TimestampedModel):
    """Teacher weekly availability schedule."""
    
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, 'Lundi'
        TUESDAY = 2, 'Mardi'
        WEDNESDAY = 3, 'Mercredi'
        THURSDAY = 4, 'Jeudi'
        FRIDAY = 5, 'Vendredi'
        SATURDAY = 6, 'Samedi'
        SUNDAY = 7, 'Dimanche'
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'teacher_availability'
        unique_together = ['teacher', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.teacher.full_name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"