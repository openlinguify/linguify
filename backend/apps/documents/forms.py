"""
Documents Forms
Custom forms for document creation and editing
"""

from django import forms
from django.contrib.auth import get_user_model
from .models.document_models import Document, Folder

User = get_user_model()


class DocumentForm(forms.ModelForm):
    """Enhanced form for document creation and editing"""
    
    class Meta:
        model = Document
        fields = [
            'title', 'content', 'content_type', 'folder', 
            'visibility', 'language', 'difficulty_level', 'tags'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de votre document',
                'maxlength': '255'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Contenu de votre document...',
                'id': 'id_content'
            }),
            'content_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_content_type'
            }),
            'folder': forms.Select(attrs={
                'class': 'form-select'
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-select'
            }),
            'language': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: fr, en, es...',
                'maxlength': '10'
            }),
            'difficulty_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Séparez les tags par des virgules',
                'maxlength': '500'
            })
        }
        
        labels = {
            'title': 'Titre du document',
            'content': 'Contenu',
            'content_type': 'Type de contenu',
            'folder': 'Dossier',
            'visibility': 'Visibilité',
            'language': 'Langue',
            'difficulty_level': 'Niveau de difficulté',
            'tags': 'Tags'
        }
        
        help_texts = {
            'title': 'Le titre de votre document (obligatoire)',
            'content': 'Le contenu principal de votre document',
            'content_type': 'Format du contenu de votre document',
            'folder': 'Dossier où organiser ce document',
            'visibility': 'Qui peut voir ce document',
            'language': 'Langue principale du document',
            'difficulty_level': 'Niveau de difficulté selon le CECRL',
            'tags': 'Mots-clés pour retrouver facilement votre document'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit folder choices to user's folders
        if self.user:
            self.fields['folder'].queryset = Folder.objects.filter(owner=self.user)
            self.fields['folder'].empty_label = "Aucun dossier"
        
        # Add required attribute to title
        self.fields['title'].required = True
        
        # Set default values
        if not self.instance.pk:  # New document
            self.fields['content_type'].initial = 'markdown'
            self.fields['visibility'].initial = 'private'
    
    def clean_title(self):
        """Validate document title"""
        title = self.cleaned_data.get('title', '').strip()
        
        if not title:
            raise forms.ValidationError("Le titre est obligatoire.")
        
        if len(title) > 255:
            raise forms.ValidationError("Le titre ne peut pas dépasser 255 caractères.")
        
        return title
    
    def clean_tags(self):
        """Clean and validate tags"""
        tags = self.cleaned_data.get('tags', '').strip()
        
        if tags:
            # Clean up tags: remove extra spaces, normalize separators
            tag_list = [tag.strip() for tag in tags.replace(';', ',').split(',')]
            tag_list = [tag for tag in tag_list if tag]  # Remove empty tags
            
            # Limit number of tags
            if len(tag_list) > 20:
                raise forms.ValidationError("Vous ne pouvez pas avoir plus de 20 tags.")
            
            # Rebuild clean tags string
            tags = ', '.join(tag_list)
        
        return tags
    
    def clean(self):
        """Additional form validation"""
        cleaned_data = super().clean()
        content = cleaned_data.get('content', '')
        content_type = cleaned_data.get('content_type', '')
        
        # Validate content based on type
        if content_type == 'html':
            # Basic HTML validation could be added here
            pass
        elif content_type == 'markdown':
            # Basic Markdown validation could be added here
            pass
        
        return cleaned_data


class FolderForm(forms.ModelForm):
    """Form for folder creation and editing"""
    
    class Meta:
        model = Folder
        fields = ['name', 'description', 'parent']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du dossier',
                'maxlength': '255'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description optionnelle du dossier...'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        
        labels = {
            'name': 'Nom du dossier',
            'description': 'Description',
            'parent': 'Dossier parent'
        }
        
        help_texts = {
            'name': 'Le nom de votre dossier (obligatoire)',
            'description': 'Description optionnelle du dossier',
            'parent': 'Dossier parent pour créer une hiérarchie'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit parent choices to user's folders (excluding self)
        if self.user:
            queryset = Folder.objects.filter(owner=self.user)
            if self.instance and self.instance.pk:
                # Exclude self and descendants to prevent circular references
                queryset = queryset.exclude(pk=self.instance.pk)
            
            self.fields['parent'].queryset = queryset
            self.fields['parent'].empty_label = "Aucun (dossier racine)"
        
        # Add required attribute
        self.fields['name'].required = True
    
    def clean_name(self):
        """Validate folder name"""
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise forms.ValidationError("Le nom du dossier est obligatoire.")
        
        if len(name) > 255:
            raise forms.ValidationError("Le nom ne peut pas dépasser 255 caractères.")
        
        # Check for duplicate names in the same parent folder
        parent = self.cleaned_data.get('parent')
        user = self.user
        
        if user:
            existing_folders = Folder.objects.filter(
                owner=user,
                parent=parent,
                name__iexact=name
            )
            
            if self.instance and self.instance.pk:
                existing_folders = existing_folders.exclude(pk=self.instance.pk)
            
            if existing_folders.exists():
                if parent:
                    raise forms.ValidationError(
                        f"Un dossier nommé '{name}' existe déjà dans le dossier '{parent.name}'."
                    )
                else:
                    raise forms.ValidationError(
                        f"Un dossier nommé '{name}' existe déjà à la racine."
                    )
        
        return name
    
    def clean_parent(self):
        """Validate parent folder to prevent circular references"""
        parent = self.cleaned_data.get('parent')
        
        if parent and self.instance and self.instance.pk:
            # Check if parent is a descendant of current folder
            current = parent
            while current:
                if current.pk == self.instance.pk:
                    raise forms.ValidationError(
                        "Un dossier ne peut pas être son propre parent ou descendant."
                    )
                current = current.parent
        
        return parent


class DocumentSearchForm(forms.Form):
    """Form for document search and filtering"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher dans les documents...',
            'autocomplete': 'off'
        }),
        label='Recherche'
    )
    
    folder = forms.ModelChoiceField(
        queryset=Folder.objects.none(),
        required=False,
        empty_label="Tous les dossiers",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Dossier'
    )
    
    visibility = forms.ChoiceField(
        choices=[('', 'Toutes les visibilités')] + Document.VISIBILITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Visibilité'
    )
    
    content_type = forms.ChoiceField(
        choices=[('', 'Tous les types')] + Document.CONTENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Type de contenu'
    )
    
    language = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ex: fr, en, es...'
        }),
        label='Langue'
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set folder choices to user's folders
        if self.user:
            self.fields['folder'].queryset = Folder.objects.filter(owner=self.user)