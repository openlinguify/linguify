from django.db import models
from authentication.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Language(models.Model):
    LANGUAGE_CHOICES = [
        English = 'EN',
        French = 'FR',
        Spanish = 'ES',
        German = 'DE',
        Italian = 'IT',
        Portuguese = 'PT',
        Dutch = 'NL',
        Russian = 'RU',
        Chinese = 'ZH',
        Japanese = 'JA',
        Korean = 'KO',
        Arabic = 'AR',
        Hindi = 'HI',
        
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=5)  # ex: EN, FR, ES
    
    def __str__(self):
        return self.name

class Coach(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    languages = models.ManyToManyField(Language, through='CoachLanguage')
    is_verified = models.BooleanField(default=False)
    commission_rate = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=15.00  # 15% commission par défaut
    )
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Coach"

class CoachLanguage(models.Model):
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    proficiency_level = models.CharField(
        max_length=2,
        choices=[
            ('A1', 'Débutant'),
            ('A2', 'Élémentaire'),
            ('B1', 'Intermédiaire'),
            ('B2', 'Intermédiaire supérieur'),
            ('C1', 'Avancé'),
            ('C2', 'Maîtrise'),
            ('NT', 'Langue maternelle')
        ]
    )
    
    class Meta:
        unique_together = ['coach', 'language']

class Booking(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_bookings')
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='coach_bookings')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    duration = models.IntegerField(help_text="Durée en minutes")
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('CONFIRMED', 'Confirmé'),
        ('COMPLETED', 'Terminé'),
        ('CANCELLED', 'Annulé'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    coach_payout = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Nouveau booking
            hourly_rate = self.coach.hourly_rate
            hours = Decimal(self.duration) / Decimal(60)
            self.total_amount = hourly_rate * hours
            self.commission_amount = self.total_amount * (self.coach.commission_rate / Decimal(100))
            self.coach_payout = self.total_amount - self.commission_amount
        super().save(*args, **kwargs)

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Mettre à jour la moyenne des notes du coach
        coach = self.booking.coach
        reviews = Review.objects.filter(booking__coach=coach)
        coach.average_rating = sum(r.rating for r in reviews) / reviews.count()
        coach.save()

class Availability(models.Model):
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(
        choices=[
            (0, 'Lundi'),
            (1, 'Mardi'),
            (2, 'Mercredi'),
            (3, 'Jeudi'),
            (4, 'Vendredi'),
            (5, 'Samedi'),
            (6, 'Dimanche'),
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        unique_together = ['coach', 'day_of_week', 'start_time', 'end_time']