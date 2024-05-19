# authentication/forms.py

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from .models import User

class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name',
                  'mother_language', 'learning_language',
                  'language_level', 'objectives', 'profile_picture']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email_qs = User.objects.filter(email=email)
            if email_qs.exists():
                raise forms.ValidationError("This email has already been registered")
        return email

class UploadProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['profile_picture']