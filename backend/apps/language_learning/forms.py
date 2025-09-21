"""
Formulaires pour l'app language_learning
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import UserLearningProfile, LanguagelearningItem, LANGUAGE_CHOICES, LEVEL_CHOICES, OBJECTIVES_CHOICES


class UserLearningProfileForm(forms.ModelForm):
    """
    Formulaire pour configurer le profil d'apprentissage des langues
    """

    class Meta:
        model = UserLearningProfile
        fields = [
            'native_language', 'target_language', 'language_level', 'objectives',
            'speaking_exercises', 'listening_exercises', 'reading_exercises', 'writing_exercises',
            'daily_goal', 'weekday_reminders', 'weekend_reminders', 'reminder_time'
        ]
        widgets = {
            'native_language': forms.Select(attrs={'class': 'form-select'}),
            'target_language': forms.Select(attrs={'class': 'form-select'}),
            'language_level': forms.Select(attrs={'class': 'form-select'}),
            'objectives': forms.Select(attrs={'class': 'form-select'}),
            'speaking_exercises': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'listening_exercises': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'reading_exercises': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'writing_exercises': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'daily_goal': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 240}),
            'weekday_reminders': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'weekend_reminders': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'reminder_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
        }
        labels = {
            'native_language': _('Your native language'),
            'target_language': _('Language you want to learn'),
            'language_level': _('Your current level'),
            'objectives': _('Your learning objectives'),
            'speaking_exercises': _('Include speaking exercises'),
            'listening_exercises': _('Include listening exercises'),
            'reading_exercises': _('Include reading exercises'),
            'writing_exercises': _('Include writing exercises'),
            'daily_goal': _('Daily goal (minutes)'),
            'weekday_reminders': _('Reminders on weekdays'),
            'weekend_reminders': _('Reminders on weekends'),
            'reminder_time': _('Reminder time'),
        }
        help_texts = {
            'daily_goal': _('How many minutes per day do you want to study?'),
            'reminder_time': _('What time would you like to receive study reminders?'),
        }

    def clean(self):
        cleaned_data = super().clean()
        native_language = cleaned_data.get('native_language')
        target_language = cleaned_data.get('target_language')

        if native_language and target_language and native_language == target_language:
            raise forms.ValidationError(_("Native language and target language cannot be the same"))

        return cleaned_data


class LanguagelearningItemForm(forms.ModelForm):
    """
    Formulaire pour créer/éditer des éléments d'apprentissage des langues
    """

    class Meta:
        model = LanguagelearningItem
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class QuickSetupForm(forms.Form):
    """
    Formulaire de configuration rapide pour les nouveaux utilisateurs
    """
    native_language = forms.ChoiceField(
        choices=[('', _('Select your native language'))] + LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Your native language')
    )

    target_language = forms.ChoiceField(
        choices=[('', _('Select the language to learn'))] + LANGUAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Language you want to learn')
    )

    language_level = forms.ChoiceField(
        choices=[('', _('Select your level'))] + LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Your current level')
    )

    objectives = forms.ChoiceField(
        choices=[('', _('Select your objectives'))] + OBJECTIVES_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Why do you want to learn this language?')
    )

    def clean(self):
        cleaned_data = super().clean()
        native_language = cleaned_data.get('native_language')
        target_language = cleaned_data.get('target_language')

        if native_language and target_language and native_language == target_language:
            raise forms.ValidationError(_("Native language and target language cannot be the same"))

        return cleaned_data


class LanguagelearningItemForm(forms.ModelForm):
    """
    Formulaire pour créer/éditer des éléments d'apprentissage des langues
    """

    class Meta:
        model = LanguagelearningItem
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }