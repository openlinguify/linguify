from django import forms
from .models import Theme

class ThemeForm(forms.Form):
    """
    A form to select a theme from a list of choices extracted from the Theme model.
    """
    theme = forms.ChoiceField(label='Sélectionnez un thème')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['theme'].choices = self.get_theme_choices()

    @staticmethod
    def get_theme_choices():
        theme_choices = Theme.objects.values_list('name', flat=True).distinct()
        return [(theme, theme) for theme in theme_choices]
