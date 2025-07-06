from django import forms
from django.utils.translation import gettext_lazy as _
from .models import JobApplication, JobPosition


class JobApplicationForm(forms.ModelForm):
    # Custom field for resume file upload
    resume_file = forms.FileField(
        required=False,
        help_text='Téléchargez votre CV (formats acceptés: PDF, DOC, DOCX, max 5MB)'
    )
    
    class Meta:
        model = JobApplication
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'cover_letter', 'resume_url',
            'portfolio_url', 'linkedin_url'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre prénom'),
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre nom de famille'),
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('votre.email@exemple.com'),
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre numéro de téléphone'),
            }),
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Expliquez pourquoi vous êtes le candidat idéal pour ce poste...'),
                'rows': 6
            }),
            'resume_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'resume_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('Lien vers votre CV en ligne (optionnel)')
            }),
            'portfolio_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('Lien vers votre portfolio (optionnel)')
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre profil LinkedIn (optionnel)')
            }),
        }
        labels = {
            'first_name': _('Prénom'),
            'last_name': _('Nom de famille'),
            'email': _('Adresse email'),
            'phone': _('Téléphone'),
            'cover_letter': _('Lettre de motivation'),
            'resume_file': _('CV (PDF, DOC, DOCX)'),
            'resume_url': _('CV en ligne'),
            'portfolio_url': _('Portfolio'),
            'linkedin_url': _('LinkedIn'),
        }
        help_texts = {
            'cover_letter': _('Présentez votre motivation et vos qualifications pour ce poste.'),
            'resume_file': _('Téléchargez votre CV (formats acceptés: PDF, DOC, DOCX, max 5MB)'),
            'resume_url': _('Si vous préférez partager un lien vers votre CV'),
            'portfolio_url': _('Lien vers vos réalisations, projets ou travaux'),
            'linkedin_url': _('Votre profil LinkedIn professionnel'),
        }

    def __init__(self, *args, **kwargs):
        self.position = kwargs.pop('position', None)
        super().__init__(*args, **kwargs)
        
        # Make cover letter required
        self.fields['cover_letter'].required = True
        
        # Custom validation messages
        self.fields['email'].error_messages = {
            'invalid': _('Veuillez saisir une adresse email valide.'),
            'required': _('L\'adresse email est obligatoire.')
        }

    def clean_resume_file(self):
        resume_file = self.cleaned_data.get('resume_file')
        if resume_file:
            # Check file size (5MB limit)
            if resume_file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_('Le fichier CV ne peut pas dépasser 5MB.'))
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_extension = resume_file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(_('Format de fichier non supporté. Veuillez utiliser PDF, DOC ou DOCX.'))
                
        return resume_file

    def clean(self):
        cleaned_data = super().clean()
        resume_file = cleaned_data.get('resume_file')
        resume_url = cleaned_data.get('resume_url')
        
        # At least one CV method must be provided
        if not resume_file and not resume_url:
            raise forms.ValidationError(_('Veuillez fournir votre CV soit en téléchargeant un fichier, soit en partageant un lien.'))
        
        return cleaned_data

    def save(self, commit=True):
        application = super().save(commit=False)
        
        # Only set position if it's a real JobPosition (not virtual for spontaneous applications)
        if self.position and hasattr(self.position, 'id') and self.position.id != 0:
            application.position = self.position
        else:
            application.position = None  # Spontaneous application
            
        application.status = 'submitted'
        
        if commit:
            application.save()
            
            # Handle resume file upload to Supabase after saving (need ID)
            resume_file = self.cleaned_data.get('resume_file')
            if resume_file:
                try:
                    success = application.upload_resume(resume_file, resume_file.name)
                    if not success:
                        # Log error but don't fail the application submission
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Failed to upload resume for application {application.id}")
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error uploading resume for application {application.id}: {str(e)}")
                    
        return application