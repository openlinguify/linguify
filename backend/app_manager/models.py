from django.db import models
from authentication.models import User

class App(models.Model):
    APP_CHOICES = (
        ('course', 'Course'),
        ('revision', 'Revision'),
        ('chat', 'Chat'),
        ('coaching', 'Coaching'),
        ('community', 'Community'),

    )
    app_name = models.CharField(max_length=100, choices=APP_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    icon_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

class UserAppAccess(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    selected_apps = models.ManyToManyField(App)
    is_premium = models.BooleanField(default=False)
    premium_expiry = models.DateTimeField(null=True, blank=True)

    @property
    def has_access_to_app(self, app_name):
        return self.selected_apps.filter(app_name=app_name).exists()
    
