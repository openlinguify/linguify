from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import Organization
from .utils import create_tenant_database
from .forms import OrganizationRegistrationForm


def register_organization(request):
    """
    Public view for organizations to register and get their own LMS instance
    """
    if request.method == 'POST':
        form = OrganizationRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create organization
                    organization = form.save()
                    
                    # Create database for organization
                    create_tenant_database(organization)
                    
                    messages.success(
                        request,
                        f'Organization "{organization.name}" registered successfully! '
                        f'You can access your LMS at: https://{organization.slug}.lms.linguify.com'
                    )
                    
                    # TODO: Send welcome email with login instructions
                    # TODO: Create initial admin user for the organization
                    
                    return redirect('tenants:registration_success')
                    
            except Exception as e:
                messages.error(
                    request,
                    f'Error creating organization: {str(e)}'
                )
    else:
        form = OrganizationRegistrationForm()
    
    return render(request, 'tenants/register.html', {
        'form': form
    })


def registration_success(request):
    """Show success page after organization registration"""
    return render(request, 'tenants/registration_success.html')