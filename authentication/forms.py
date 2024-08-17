from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.core.exceptions import ValidationError
from .models import User, TeacherProfile, StudentProfile

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['user_type', 'username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("This email has already been registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise ValidationError("This username has already been registered.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        profile_picture = cleaned_data.get('profile_picture')

        if user_type == 'student' and profile_picture:
            raise ValidationError("Student accounts cannot have a profile picture during signup.")
        
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
        fields = ['address', 'mother_language', 'learning_language', 'language_level', 'objectives', 'profile_picture']

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            width, height = get_image_dimensions(profile_picture)
            if width > 500 or height > 500:
                raise ValidationError("The profile picture should not exceed 500x500 pixels.")
        return profile_picture


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['profile_picture', 'presentation', 'mother_language', 'meeting_type', 'price_per_hour', 'availability']

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            width, height = get_image_dimensions(profile_picture)
            if width > 500 or height > 500:
                raise ValidationError("The profile picture should not exceed 500x500 pixels.")
        return profile_picture


class UploadStudentProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['profile_picture']

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            width, height = get_image_dimensions(profile_picture)
            if width > 500 or height > 500:
                raise ValidationError("The profile picture should not exceed 500x500 pixels.")
        return profile_picture


class UploadTeacherProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['profile_picture']

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            width, height = get_image_dimensions(profile_picture)
            if width > 500 or height > 500:
                raise ValidationError("The profile picture should not exceed 500x500 pixels.")
        return profile_picture


class TeacherRegistrationForm(UserCreationForm):
    """
    Form for teacher registration, extending the default UserCreationForm with additional teacher-specific fields.
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True  # Set the user as a teacher
        if commit:
            user.save()
            TeacherProfile.objects.create(user=user)  # Create a corresponding TeacherProfile
        return user
