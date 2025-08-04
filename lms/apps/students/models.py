from django.db import models
from django.conf import settings


class StudentProfile(models.Model):
    """
    Profil etudiant avec informations academiques
    """
    YEAR_CHOICES = [
        ('1', 'Premiere annee'),
        ('2', 'Deuxieme annee'), 
        ('3', 'Troisieme annee'),
        ('4', 'Quatrieme annee'),
        ('5', 'Cinquieme annee'),
        ('graduate', 'Etudes superieures'),
        ('phd', 'Doctorat'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('graduated', 'Diplome'),
        ('withdrawn', 'Retire'),
    ]
    
    STUDY_MODE_CHOICES = [
        ('full_time', 'Temps plein'),
        ('part_time', 'Temps partiel'),
        ('distance', 'A distance'),
    ]
    
    # Lien vers l'utilisateur
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    
    # Informations academiques
    student_id = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Numero d'etudiant unique"
    )
    
    # Institution (organisation ID stocké comme string)
    organization_id = models.CharField(
        max_length=50,
        default='unknown',
        help_text="ID de l'organisation (automatiquement defini)"
    )
    
    # Annee d'etudes
    academic_year = models.CharField(
        max_length=10,
        choices=YEAR_CHOICES,
        default='1'
    )
    
    # Programme d'etudes
    program = models.CharField(
        max_length=100,
        help_text="Ex: Informatique, Droit, Medecine..."
    )
    
    # Specialisation
    specialization = models.CharField(
        max_length=100,
        blank=True,
        help_text="Specialisation ou concentration"
    )
    
    # Dates importantes
    enrollment_date = models.DateField(
        help_text="Date d'inscription"
    )
    expected_graduation = models.DateField(
        null=True, blank=True,
        help_text="Date de diplome prevue"
    )
    
    # Statut academique
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Mode d'etude
    study_mode = models.CharField(
        max_length=20,
        choices=STUDY_MODE_CHOICES,
        default='full_time'
    )
    
    # Moyenne generale
    gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True, blank=True,
        help_text="Moyenne generale (ex: 3.75)"
    )
    
    # Credits
    credits_earned = models.PositiveIntegerField(
        default=0,
        help_text="Credits obtenus"
    )
    credits_required = models.PositiveIntegerField(
        default=120,
        help_text="Credits requis pour le diplome"
    )
    
    # Contact d'urgence
    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True
    )
    emergency_contact_relation = models.CharField(
        max_length=50,
        blank=True,
        help_text="Ex: Parent, Conjoint, Ami..."
    )
    
    # Metadonnees
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil Etudiant"
        verbose_name_plural = "Profils Etudiants"
        ordering = ['student_id']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id}"
    
    @property
    def progress_percentage(self):
        """Calcule le pourcentage de progression vers le diplome"""
        if self.credits_required > 0:
            return min((self.credits_earned / self.credits_required) * 100, 100)
        return 0
    
    @property
    def is_active(self):
        """Verifie si l'etudiant est actif"""
        return self.status == 'active'


class CourseEnrollment(models.Model):
    """
    Inscription d'un etudiant a un cours
    """
    ENROLLMENT_STATUS_CHOICES = [
        ('enrolled', 'Inscrit'),
        ('completed', 'Termine'),
        ('dropped', 'Abandonne'),
        ('failed', 'Echoue'),
        ('audit', 'Auditeur'),
    ]
    
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    # Note: On aura besoin du modele Course plus tard
    course_id = models.CharField(
        max_length=50,
        help_text="ID du cours (en attendant le modele Course)"
    )
    course_name = models.CharField(
        max_length=200,
        help_text="Nom du cours"
    )
    
    # Statut d'inscription
    status = models.CharField(
        max_length=20,
        choices=ENROLLMENT_STATUS_CHOICES,
        default='enrolled'
    )
    
    # Dates
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Note finale
    final_grade = models.CharField(
        max_length=5,
        blank=True,
        help_text="Note finale (A, B, C, D, F ou numerique)"
    )
    
    # Points de credit pour ce cours
    credits = models.PositiveIntegerField(default=3)
    
    class Meta:
        verbose_name = "Inscription au Cours"
        verbose_name_plural = "Inscriptions aux Cours"
        unique_together = ['student', 'course_id']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.course_name}"