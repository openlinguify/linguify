"""
Course creation and management forms.
"""
from django import forms
from .models import CMSUnit


class CourseCreateForm(forms.ModelForm):
    """Form for creating new courses with automatic translation."""
    
    class Meta:
        model = CMSUnit
        fields = [
            'title_fr', 'description_fr',
            'category', 'level', 'price', 'duration_hours'
        ]
        
        widgets = {
            'title_fr': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de votre cours en français',
                'required': True
            }),
            'description_fr': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée de votre cours en français'
            }),
            'category': forms.HiddenInput(),
            'level': forms.HiddenInput(),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '10',
                'min': '1',
                'max': '500'
            }),
        }
        
        labels = {
            'title_fr': 'Titre du cours',
            'description_fr': 'Description du cours',
            'price': 'Prix (€)',
            'duration_hours': 'Durée estimée (heures)',
        }
    
    def clean_title_fr(self):
        """Ensure French title is provided."""
        title_fr = self.cleaned_data.get('title_fr')
        if not title_fr:
            raise forms.ValidationError('Le titre en français est obligatoire.')
        return title_fr
    
    def clean_price(self):
        """Ensure price is positive."""
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Le prix ne peut pas être négatif.')
        return price
    
    def clean(self):
        """Validate category and level are selected."""
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        level = cleaned_data.get('level')
        
        if not category:
            raise forms.ValidationError('Veuillez sélectionner une catégorie.')
        
        if not level:
            raise forms.ValidationError('Veuillez sélectionner un niveau.')
        
        return cleaned_data