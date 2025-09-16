# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Formulaires d'authentification

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from ..models.models import LANGUAGE_CHOICES, LEVEL_CHOICES, OBJECTIVES_CHOICES

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
    
    native_language = forms.ChoiceField(
        choices=[('', _('Select your native language'))] + LANGUAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('Your native language')
    )
    
    target_language = forms.ChoiceField(
        choices=[('', _('Select the language to learn'))] + LANGUAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('Language you want to learn')
    )
    
    language_level = forms.ChoiceField(
        choices=[('', _('Select your level'))] + LEVEL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('Current language level')
    )
    
    objectives = forms.ChoiceField(
        choices=[('', _('Select your objectives'))] + OBJECTIVES_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label=_('Learning objectives')
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
            'birthday', 'gender', 'password1', 'password2', 'native_language',
            'target_language', 'language_level', 'objectives', 'terms'
        )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            from ..utils.validators import is_username_available
            result = is_username_available(username)
            if not result['available']:
                raise forms.ValidationError(result['message'])
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        native_language = cleaned_data.get('native_language')
        target_language = cleaned_data.get('target_language')
        
        if native_language and target_language and native_language == target_language:
            raise forms.ValidationError(_("Native language and target language cannot be the same"))
        
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
        user.native_language = self.cleaned_data['native_language']
        user.target_language = self.cleaned_data['target_language']
        user.language_level = self.cleaned_data['language_level']
        user.objectives = self.cleaned_data['objectives']

        # Enregistrer l'acceptation des termes si cochée
        if self.cleaned_data.get('terms'):
            user.terms_accepted = True
            user.terms_accepted_at = timezone.now()
            user.terms_version = getattr(settings, 'TERMS_VERSION', '1.0')

        if commit:
            user.save()
        return user