"""
Django template-based authentication views
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils.translation import gettext as _


class LoginView(FormView):
    """Login view using Django templates"""
    template_name = 'authentication/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('saas_web:dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to dashboard
        if request.user.is_authenticated:
            return redirect('saas_web:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(self.request, user)
            messages.success(self.request, _('Welcome, %(username)s!') % {'username': user.username})
            
            # Redirect to next page if specified
            next_page = self.request.GET.get('next')
            if next_page:
                return HttpResponseRedirect(next_page)
            
            return super().form_valid(form)
        else:
            # Add error to the form itself
            error_message = _('Invalid username or password.')
            form.add_error(None, error_message)
            messages.error(self.request, error_message)
            return self.form_invalid(form)


class RegisterView(FormView):
    """Register view using Django templates"""
    template_name = 'authentication/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('auth:login')
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to dashboard
        if request.user.is_authenticated:
            return redirect('saas_web:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        username = form.cleaned_data.get('username')
        messages.success(
            self.request, 
            f'Compte créé avec succès pour {username}! Vous pouvez maintenant vous connecter.'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)


def logout_view(request):
    """Simple logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('public_web:landing')