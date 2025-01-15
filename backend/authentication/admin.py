from django.contrib import admin
from .models import User, CoachProfile, Review, UserFeedback
# Register your models here.

admin.site.register(User)
admin.site.register(CoachProfile)
admin.site.register(Review)
admin.site.register(UserFeedback)
