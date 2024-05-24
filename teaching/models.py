from django.db import models
from authentication.models import User
# Create your models here.

class Meeting_type(models.TextChoices):
    ONLINE = 'online', 'Online'
    IN_PERSON = 'face_to_face', 'Face to Face'

class Price(models.Model):
    CURRENCY_CHOICES = (
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    )

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    profile_picture = models.ImageField(verbose_name='Profile Picture')
    mother_language = models.CharField(max_length=50, choices=Language.choices, default=Language.ENGLISH, null=True, blank=True)
    # insert a bio field
    bio = models.TextField(max_length=500, null=True, blank=True)
    price_hourly = models.DecimalField(max_digits=5, decimal_places=2, default=0, max_value=150.00)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    meeting_type = models.CharField(max_length=50, choices=Meeting_type.choices, default=Meeting_type.ONLINE, null=True, blank=True)
    verified_profile = models.BooleanField(default=False)

class Schedule(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE)
    day = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} - {self.last_name}"


class Earnings(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0, max_value=10000.00)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, max_value=1000.00)
    total_students = models.IntegerField(default=0)
    total_lessons = models.IntegerField(default=0)
    total_reviews = models.IntegerField(default=0)
    total_ratings = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, max_value=5.00)

    def __str__(self):
        return f"{self.teacher.first_name} - {self.teacher.last_name}"

class Review(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    review_content = models.TextField(max_length=500)
    review_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.teacher.first_name} - {self.student.first_name}"





