# teaching/models.py
from django.db import models
from django.contrib.auth.models import User
from authentication.models import  import Language

CHOICE_LANGUAGE = (
    ('EN', 'English'),
    ('FR', 'French'),
    ('DE', 'German'),
    ('ES', 'Spanish'),
    ('IT', 'Italian'),
)

class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    language = models.CharField(max_length=2, choices=Language.choices)  # Utilisation de Language
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hourly_rate = models.DecimalField(max_digits=5, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    def get_students(self):
        return Selection.objects.filter(teacher=self)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['last_name', 'first_name']


class Selection(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    language = models.CharField(max_length=2, choices=Language.choices)  # Utilisation de Language
    duration = models.IntegerField()
    selected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.teacher} - {self.student} - {self.date}'

    class Meta:
        ordering = ['date']

