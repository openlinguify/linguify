from django import forms
from .models import LanguagelearningItem


class LanguagelearningItemForm(forms.ModelForm):
    """Formulaire pour créer/modifier un item Language Learning"""
    
    class Meta:
        model = LanguagelearningItem
        fields = ['title', 'description', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de l\'item'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description de l\'item'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Titre',
            'description': 'Description',
            'is_active': 'Actif'
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or len(title.strip()) < 3:
            raise forms.ValidationError('Le titre doit contenir au moins 3 caractères.')
        return title.strip()
