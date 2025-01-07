# app_manager/models.py
from django.db import models
from django.apps import apps
from authentication.models import User

class AppModule(models.Model):
    name = models.CharField(max_length=100)  # Nom technique de l'app Django
    display_name = models.CharField(max_length=100)  # Nom affiché
    description = models.TextField()
    icon_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    def get_app_model(self):
        """Récupère le modèle principal de l'application"""
        try:
            # Par exemple, si l'app 'course' a un modèle 'Course'
            return apps.get_model(self.name, self.name.capitalize())
        except LookupError:
            return None

    class Meta:
        ordering = ['order']

class UserAppAccess(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    free_selected_app = models.ForeignKey(
        AppModule, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='free_users'
    )
    is_premium = models.BooleanField(default=False)
    premium_expiry = models.DateTimeField(null=True, blank=True)
