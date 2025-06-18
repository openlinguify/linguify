from django.db import models
from django.utils import timezone
from .storage import jobs_supabase_storage
import logging

logger = logging.getLogger(__name__)


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['name']
        db_table = 'jobs_department'
    
    def __str__(self):
        return self.name


class JobPosition(models.Model):
    EMPLOYMENT_TYPES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('lead', 'Lead'),
        ('manager', 'Manager'),
    ]
    
    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    location = models.CharField(max_length=200)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='mid')
    
    # Job Details
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField()
    benefits = models.TextField(blank=True)
    
    # Salary (optional)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='EUR')
    
    # Application
    application_email = models.EmailField()
    application_url = models.URLField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Dates
    posted_date = models.DateTimeField(default=timezone.now)
    closing_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-posted_date', '-is_featured']
        db_table = 'jobs_jobposition'
        indexes = [
            models.Index(fields=['is_active', 'posted_date']),
            models.Index(fields=['department', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.location}"
    
    @property
    def is_open(self):
        """Check if the position is still open for applications"""
        if not self.is_active:
            return False
        if self.closing_date and self.closing_date < timezone.now():
            return False
        return True
    
    @property
    def salary_range(self):
        """Get formatted salary range"""
        if self.salary_min and self.salary_max:
            return f"{self.salary_min:,.0f} - {self.salary_max:,.0f} {self.salary_currency}"
        elif self.salary_min:
            return f"From {self.salary_min:,.0f} {self.salary_currency}"
        return None


class JobApplication(models.Model):
    STATUSES = [
        ('submitted', 'Submitted'),
        ('reviewed', 'Under Review'),
        ('interview', 'Interview Stage'),
        ('offer', 'Offer Extended'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='applications', null=True, blank=True)
    
    # Applicant Details
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Application Materials
    cover_letter = models.TextField(blank=True)
    resume_file_path = models.CharField(max_length=500, blank=True, null=True)  # Chemin dans Supabase
    resume_original_filename = models.CharField(max_length=255, blank=True, null=True)  # Nom original du fichier
    resume_content_type = models.CharField(max_length=100, blank=True, null=True)  # Type MIME
    resume_url = models.URLField(blank=True)  # URL externe si fournie par le candidat
    portfolio_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Status & Tracking
    status = models.CharField(max_length=20, choices=STATUSES, default='submitted')
    notes = models.TextField(blank=True)
    
    # Dates
    applied_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-applied_at']
        db_table = 'jobs_jobapplication'
        # Note: Removed unique_together to allow spontaneous applications
    
    def __str__(self):
        position_title = self.position.title if self.position else "Candidature spontanée"
        return f"{self.first_name} {self.last_name} - {position_title}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def upload_resume(self, file, original_filename: str = None):
        """
        Upload un CV vers Supabase Storage
        
        Args:
            file: Fichier à uploader
            original_filename: Nom original du fichier (optionnel)
        
        Returns:
            bool: True si l'upload réussit, False sinon
        """
        try:
            if not original_filename:
                original_filename = getattr(file, 'name', 'resume.pdf')
            
            result = jobs_supabase_storage.upload_resume(
                str(self.id),
                file,
                original_filename
            )
            
            if result['success']:
                self.resume_file_path = result['file_path']
                self.resume_original_filename = result['original_filename']
                self.resume_content_type = result['content_type']
                self.save(update_fields=['resume_file_path', 'resume_original_filename', 'resume_content_type'])
                logger.info(f"Resume uploaded successfully for application {self.id}")
                return True
            else:
                logger.error(f"Failed to upload resume for application {self.id}: {result['error']}")
                return False
                
        except Exception as e:
            logger.exception(f"Error uploading resume for application {self.id}: {str(e)}")
            return False
    
    def get_resume_download_url(self, expires_in: int = 3600):
        """
        Génère une URL de téléchargement sécurisée pour le CV
        
        Args:
            expires_in: Durée de validité en secondes (défaut: 1 heure)
            
        Returns:
            str: URL de téléchargement ou None si pas de CV
        """
        if not self.resume_file_path:
            return None
            
        return jobs_supabase_storage.get_resume_download_url(
            self.resume_file_path,
            expires_in
        )
    
    def has_resume(self):
        """Vérifie si l'application a un CV uploadé"""
        return bool(self.resume_file_path)
    
    def delete_resume(self):
        """Supprime le CV de Supabase Storage"""
        if self.resume_file_path:
            try:
                success = jobs_supabase_storage.delete_resume(self.resume_file_path)
                if success:
                    self.resume_file_path = None
                    self.resume_original_filename = None
                    self.resume_content_type = None
                    self.save(update_fields=['resume_file_path', 'resume_original_filename', 'resume_content_type'])
                    logger.info(f"Resume deleted successfully for application {self.id}")
                return success
            except Exception as e:
                logger.exception(f"Error deleting resume for application {self.id}: {str(e)}")
                return False
        return True
    
    def delete(self, *args, **kwargs):
        """Override delete pour supprimer les fichiers associés"""
        # Supprimer les fichiers avant de supprimer l'enregistrement
        if self.resume_file_path:
            jobs_supabase_storage.delete_application_files(str(self.id))
        super().delete(*args, **kwargs)