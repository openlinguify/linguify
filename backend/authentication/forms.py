from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.core.exceptions import ValidationError
from .models import User, Teacherprofile, StudentProfile

# Getting the user model
User = get_user_model()

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['user_type', 'username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        if user_type == 'student' and cleaned_data.get('profile_picture'):
            raise ValidationError('Student accounts cannot have a profile picture.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.cleaned_data.get('user_type')
        if commit:
            user.save()
        return user


class BaseProfileForm(forms.ModelForm):
    """Base form for common profile fields."""
    class Meta:
        abstract = True


class StudentProfileForm(BaseProfileForm):
    class Meta:
        model = StudentProfile
        fields = ['address', 'mother_language', 'learning_language', 'language_level', 'objectives', 'profile_picture']


class TeacherProfileForm(BaseProfileForm):
    class Meta:
        model = Teacherprofile
        fields = ['profile_picture', 'presentation', 'mother_language', 'meeting_type', 'price_per_hour', 'availability']


class UploadStudentProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['profile_picture']


class UploadTeacherProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = Teacherprofile
        fields = ['profile_picture']
