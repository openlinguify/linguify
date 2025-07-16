# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Formulaires d'authentification

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
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
            'placeholder': 'Votre prénom'
        }),
        label="Prénom"
    )
    
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Votre nom'
        }),
        label="Nom"
    )
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'nom_utilisateur'
        }),
        label="Nom d'utilisateur"
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'votre@email.com'
        }),
        label="Adresse email"
    )
    
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+33 6 12 34 56 78'
        }),
        label="Numéro de téléphone",
        help_text="Optionnel - pour la récupération de compte"
    )
    
    birthday = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        }),
        label="Date de naissance"
    )
    
    gender = forms.ChoiceField(
        choices=[
            ('', 'Sélectionnez votre genre'),
            ('M', 'Homme'),
            ('F', 'Femme'),
            ('O', 'Autre'),
            ('N', 'Préfère ne pas dire')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Genre"
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Mot de passe'
        }),
        label="Mot de passe"
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirmer le mot de passe'
        }),
        label="Confirmer le mot de passe"
    )
    
    native_language = forms.ChoiceField(
        choices=[('', 'Sélectionnez votre langue native')] + LANGUAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Votre langue native"
    )
    
    target_language = forms.ChoiceField(
        choices=[('', 'Sélectionnez la langue à apprendre')] + LANGUAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Langue que vous souhaitez apprendre"
    )
    
    language_level = forms.ChoiceField(
        choices=[('', 'Sélectionnez votre niveau')] + LEVEL_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Niveau de langue actuel"
    )
    
    objectives = forms.ChoiceField(
        choices=[('', 'Sélectionnez vos objectifs')] + OBJECTIVES_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Objectifs d'apprentissage"
    )
    
    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox'
        }),
        label="J'accepte les conditions d'utilisation"
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
            raise forms.ValidationError("La langue native et la langue cible ne peuvent pas être identiques.")
        
        return cleaned_data
    
    def save(self, commit=True):
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
        
        if commit:
            user.save()
        return user