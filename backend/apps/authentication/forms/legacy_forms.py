"""
Custom forms for authentication app
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model()


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form that allows login with email or username
    """
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'placeholder': _('Email or Username'),
            'class': 'form-control'
        }),
        label=_('Email or Username')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update the username field to be more generic
        self.fields['username'].label = _('Email or Username')
        self.fields['username'].help_text = _('You can use either your email address or username to log in.')
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            # Use our custom authentication backend
            self.user_cache = authenticate(
                self.request, 
                username=username, 
                password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
    
    def get_invalid_login_error(self):
        return forms.ValidationError(
            _('Please enter a correct email/username and password. Note that both fields may be case-sensitive.'),
            code='invalid_login',
            params={'username': self.username_field.verbose_name},
        )


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form that uses our User model"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+32 123 456 789'
        }),
        label="Numéro de téléphone",
        help_text="Optionnel. Format: +32 123 456 789"
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    birthday = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        label="Date de naissance"
    )
    gender = forms.ChoiceField(
        choices=[('', 'Choisir votre genre')] + list(User._meta.get_field('gender').choices),
        required=False,
        label="Genre",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    native_language = forms.ChoiceField(
        choices=[('', 'Choisir votre langue native')] + list(User._meta.get_field('native_language').choices),
        required=True,
        label="Langue native",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    target_language = forms.ChoiceField(
        choices=[('', 'Choisir la langue à apprendre')] + list(User._meta.get_field('target_language').choices),
        required=True,
        label="Langue à apprendre",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    language_level = forms.ChoiceField(
        choices=[('', 'Choisir votre niveau')] + list(User._meta.get_field('language_level').choices),
        required=False,
        label="Niveau de langue actuel",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    objectives = forms.ChoiceField(
        choices=[('', 'Choisir vos objectifs')] + list(User._meta.get_field('objectives').choices),
        required=False,
        label="Objectifs d'apprentissage",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    terms = forms.BooleanField(
        required=True, 
        label="J'accepte les conditions d'utilisation",
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'first_name', 'last_name', 'birthday', 'gender', 'password1', 'password2', 'native_language', 'target_language', 'language_level', 'objectives', 'terms')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom CSS classes to inherited fields
        self.fields['username'].widget.attrs.update({'class': 'form-input'})
        self.fields['password1'].widget.attrs.update({'class': 'form-input'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input'})
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            from .utils.validators import validate_username_complete
            try:
                username = validate_username_complete(username)
            except ValidationError as e:
                raise forms.ValidationError(str(e))
        return username
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Basic validation for international phone format
            import re
            # Allow + followed by digits, spaces, dashes, parentheses
            pattern = r'^\+\d{1,4}[\s\-\(\)]*[\d\s\-\(\)]{8,}$'
            if not re.match(pattern, phone_number.strip()):
                raise forms.ValidationError(
                    'Please enter a valid phone number with country code (e.g., +32 123 456 789)'
                )
        return phone_number
    
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
            phone_number=self.cleaned_data.get('phone_number'),
            birthday=self.cleaned_data.get('birthday'),
            gender=self.cleaned_data.get('gender'),
            native_language=self.cleaned_data['native_language'],
            target_language=self.cleaned_data['target_language'],
            language_level=self.cleaned_data.get('language_level'),
            objectives=self.cleaned_data.get('objectives'),
        )
        
        # Handle terms acceptance
        if self.cleaned_data.get('terms'):
            user.terms_accepted = True
            user.terms_accepted_at = timezone.now()
            user.terms_version = 'v1.0'
            user.save()
        
        return user