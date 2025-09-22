# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Formulaires d'authentification

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from ..models.models import DuplicateEmailError

User = get_user_model()

class LoginForm(AuthenticationForm):
    """Formulaire de connexion"""
    pass

class RegisterForm(UserCreationForm):
    """Formulaire d'inscription complet"""
    
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('Your first name')
        }),
        label=_('First name')
    )
    
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('Your last name')
        }),
        label=_('Last name')
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('username')
        }),
        label=_('Username')
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': _('your@email.com')
        }),
        label=_('Email address')
    )
    
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+33 6 12 34 56 78'
        }),
        label=_('Phone number'),
        help_text=_('Optional - for account recovery')
    )
    
    birthday = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        }),
        label=_('Date of birth')
    )
    
    gender = forms.ChoiceField(
        choices=[
            ('', _('Select your gender')),
            ('M', _('Male')),
            ('F', _('Female')),
            ('O', _('Other')),
            ('N', _('Prefer not to say'))
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('Gender')
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': _('Password')
        }),
        label=_('Password')
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': _('Confirm password')
        }),
        label=_('Confirm password')
    )
    
    interface_language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        initial='en',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('Interface language'),
        help_text=_('Choose the language for the application interface')
    )

    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        }),
        label=_('I accept the terms of use and privacy policy')
    )
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'email', 'phone_number',
            'birthday', 'gender', 'interface_language', 'password1', 'password2', 'terms'
        )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            from ..utils.validators import is_username_available
            result = is_username_available(username)
            if not result['available']:
                raise forms.ValidationError(result['message'])
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Vérifier les domaines temporaires/jetables communs
            disposable_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com', 'mailinator.com']
            domain = email.split('@')[-1].lower()
            if domain in disposable_domains:
                raise forms.ValidationError(_("Please use a permanent email address"))

            # Vérifier les emails existants avec DuplicateEmailError
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if User.objects.filter(email=email).exists():
                # Utiliser DuplicateEmailError pour une meilleure traçabilité
                error = DuplicateEmailError(
                    message=_("An account with this email already exists. Please use a different email or login with your existing account."),
                    email=email
                )
                # Log l'erreur pour le monitoring
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Registration attempt with duplicate email: {email}")

                # Convertir en ValidationError pour le formulaire
                raise forms.ValidationError(error.message)
        return email

    def clean(self):
        cleaned_data = super().clean()

        # Validation des termes avec message explicite
        terms_accepted = cleaned_data.get('terms')
        if not terms_accepted:
            raise forms.ValidationError(_("You must accept the terms and conditions to create an account"))

        return cleaned_data
    
    def save(self, commit=True):
        from django.utils import timezone
        from django.conf import settings

        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.birthday = self.cleaned_data['birthday']
        user.gender = self.cleaned_data['gender']
        user.interface_language = self.cleaned_data['interface_language']

        # Enregistrer l'acceptation des termes si cochée
        if self.cleaned_data.get('terms'):
            user.terms_accepted = True
            user.terms_accepted_at = timezone.now()
            user.terms_version = getattr(settings, 'TERMS_VERSION', '1.0')

        if commit:
            user.save()
        return user