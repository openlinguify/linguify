from django.contrib import admin
from authentication.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
class CustomerUserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'mother_language', 'learning_language', 'is_staff', 'is_active', 'date_joined', 'role', 'objectives', 'level_target_language')

class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'mother_language', 'learning_language', 'is_staff', 'is_active', 'date_joined', 'role', 'objectives', 'level_target_language')

admin.site.unregister(User)
admin.site.register(User, CustomerUserAdmin)
