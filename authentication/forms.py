# authentication/forms.py

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from .models import User, TeacherProfile, StudentProfile

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['user_type', 'username', 'email', 'password1', 'password2', ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email_qs = User.objects.filter(email=email)
            if email_qs.exists():
                raise forms.ValidationError("This email has already been registered")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username_qs = User.objects.filter(username=username)
            if username_qs.exists():
                raise forms.ValidationError("This username has already been registered")
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
class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['address', 'mother_language','learning_language', 'language_level', 'objectives', 'profile_picture']
class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['profile_picture', 'presentation', 'mother_language', 'meeting_type', 'price_per_hour', 'availability']

class UploadStudentProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['profile_picture']

class UploadTeacherProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['profile_picture']
