# linguify/forms.py
from django import forms
from .models import Revision

class ThemeForm(forms.ModelForm):
    """
    A form to select a theme from a list of choices extracted from the Revision model.
    """
    class Meta:
        model = Revision
        fields = ['theme']
        labels = {
            'theme': 'Sélectionnez un thème'
        }
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Sélectionnez un thème'})
        }

    def __init__(self, *args, **kwargs):
        super(ThemeForm, self).__init__(*args, **kwargs)
        self.fields['theme'].queryset = Revision.objects.values_list('theme', flat=True).distinct()
        self.fields['theme'].empty_label = "Choisissez un thème"
        self.fields['theme'].help_text = "Veuillez choisir un thème parmi ceux disponibles."

# Improvements Summary:
# 1. Switched to ModelForm to reduce boilerplate code and improve maintainability.
# 2. Directly linked fields with the model to simplify form handling.
# 3. Added a 'Meta' class to better define model relationships and labels.
# 4. Added an empty label for the 'theme' field to improve user experience.
# 5. Added a widget for the 'theme' field to apply consistent styling.
# 6. Added a placeholder and help text to improve user guidance.