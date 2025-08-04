from django import forms
from django.utils.text import slugify
from .models import Organization


class OrganizationRegistrationForm(forms.ModelForm):
    """Form for organizations to register for LMS"""
    
    admin_email = forms.EmailField(
        label='Administrator Email',
        help_text='Email for the main administrator account'
    )
    
    admin_password = forms.CharField(
        widget=forms.PasswordInput,
        label='Administrator Password'
    )
    
    admin_password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label='Confirm Password'
    )
    
    terms_accepted = forms.BooleanField(
        label='I accept the terms and conditions'
    )
    
    class Meta:
        model = Organization
        fields = ['name', 'email', 'phone', 'address', 'country']
        
    def clean_slug(self):
        """Auto-generate slug from name"""
        name = self.cleaned_data.get('name')
        if name:
            slug = slugify(name)
            # Ensure unique slug
            base_slug = slug
            counter = 1
            while Organization.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            return slug
        return None
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('admin_password')
        password_confirm = cleaned_data.get('admin_password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save organization with generated slug"""
        instance = super().save(commit=False)
        instance.slug = self.clean_slug()
        if commit:
            instance.save()
        return instance