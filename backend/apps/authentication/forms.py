"""
Custom forms for authentication app
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form that uses our User model"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    native_language = forms.ChoiceField(
        choices=[('', 'Choisir votre langue native')] + list(User._meta.get_field('native_language').choices),
        required=True,
        label="Langue native"
    )
    target_language = forms.ChoiceField(
        choices=[('', 'Choisir la langue à apprendre')] + list(User._meta.get_field('target_language').choices),
        required=True,
        label="Langue à apprendre"
    )
    terms = forms.BooleanField(required=True, label="J'accepte les conditions d'utilisation")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'native_language', 'target_language', 'terms')
    
    def clean(self):
        cleaned_data = super().clean()
        native_language = cleaned_data.get('native_language')
        target_language = cleaned_data.get('target_language')
        
        if native_language and target_language and native_language == target_language:
            raise forms.ValidationError("La langue native et la langue cible ne peuvent pas être identiques.")
        
        return cleaned_data
    
    def save(self, commit=True):
        # Use User.objects.create_user() which is how Django admin works
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            native_language=self.cleaned_data['native_language'],
            target_language=self.cleaned_data['target_language'],
        )
        
        # Handle terms acceptance
        if self.cleaned_data.get('terms'):
            user.terms_accepted = True
            from django.utils import timezone
            user.terms_accepted_at = timezone.now()
            user.terms_version = 'v1.0'
            user.save()
        
        return user