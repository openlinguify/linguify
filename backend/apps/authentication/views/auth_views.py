# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Vues d'authentification
from django.contrib.auth import views as auth_views, login
from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext as _
from ..forms.auth_forms import RegisterForm
from ..services.email_service import EmailVerificationService
from ..security.rate_limiter import EmailVerificationRateLimiter, rate_limit_response
from ..security.audit_logger import SecurityAuditLogger

class LoginView(auth_views.LoginView):
    """Login View"""
    template_name = 'authentication/login.html'
    
    def form_valid(self, form):
        """Override to check if user is verified"""
        user = form.get_user()
        
        if not user.is_active:
            # User exists but is not verified
            messages.error(
                self.request, 
                _('Your email address is not verified yet. Please check your email and click the verification link.')
            )
            return redirect(f'/auth/email-verification-waiting/?email={user.email}')
        
        # User is verified, proceed with normal login
        response = super().form_valid(form)
        messages.success(self.request, _('Welcome back!'))
        return response

class RegisterView(View):
    """Register View"""
    
    def get(self, request):
        form = RegisterForm()
        return render(request, 'authentication/register.html', {'form': form})
    
    def post(self, request):
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            client_ip = EmailVerificationRateLimiter.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            try:
                user = form.save()
                
                # Log registration
                SecurityAuditLogger.log_registration(user, client_ip, user_agent)
                
                # Set interface language from current session language or native language
                current_language = getattr(request, 'LANGUAGE_CODE', 'en')
                native_language = user.native_language or current_language
                
                # Map native language codes to interface language codes if needed
                language_mapping = {
                    'EN': 'en', 'FR': 'fr', 'ES': 'es', 'NL': 'nl', 
                    'DE': 'de', 'IT': 'it', 'PT': 'pt'
                }
                interface_lang = language_mapping.get(native_language.upper(), current_language)
                
                user.interface_language = interface_lang
                user.save()
                
                # Send verification email
                try:
                    token = EmailVerificationService.create_verification_token(user)
                    email_sent = EmailVerificationService.send_verification_email(user, token, request)
                    
                    if email_sent:
                        SecurityAuditLogger.log_email_verification_sent(user, token.id, client_ip)
                    
                    messages.success(request, _('Account created successfully! Please check your email to verify your account.'))
                    return redirect(f'/auth/email-verification-waiting/?email={user.email}')
                        
                except Exception as email_error:
                    SecurityAuditLogger.log_suspicious_activity(
                        user.email, 
                        f'Email sending failed: {str(email_error)}', 
                        client_ip, 
                        'ERROR'
                    )
                    messages.error(request, _('Account created but failed to send verification email. Please contact support.'))
                    
            except Exception as e:
                SecurityAuditLogger.log_suspicious_activity(
                    request.POST.get('email', 'unknown'), 
                    f'Registration failed: {str(e)}', 
                    client_ip, 
                    'ERROR'
                )
                messages.error(request, _('An error occurred while creating your account. Please try again.'))
        
        return render(request, 'authentication/register.html', {'form': form})

def logout_view(request):
    """Log Out View"""
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    from django.contrib import messages
    from django.conf import settings
    
    # Effectuer la déconnexion
    logout(request)
    
    # Message de succès
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    
    # Rediriger vers le portal
    portal_url = 'http://127.0.0.1:8080' if settings.DEBUG else 'https://openlinguify.com'
    return redirect(portal_url)


class EmailVerificationWaitingView(View):
    """View shown after registration while waiting for email verification"""
    
    def get(self, request):
        email = request.GET.get('email', '')
        return render(request, 'authentication/emails/email_verification_waiting.html', {
            'email': email
        })


def verify_email_view(request, token):
    """View to verify email with token"""
    # Get client IP for rate limiting
    client_ip = EmailVerificationRateLimiter.get_client_ip(request)
    
    # Basic token validation first
    if not token or len(token) != 64:
        return render(request, 'authentication/emails/email_verification_error.html', {
            'error': 'invalid_token'
        })
    
    result = EmailVerificationService.verify_token(token)
    
    if result['success']:
        user = result['user']
        
        # Check rate limits for this user
        allowed, remaining, reset_time = EmailVerificationRateLimiter.check_verification_attempts(
            user.email, client_ip
        )
        
        if not allowed:
            EmailVerificationRateLimiter.record_verification_attempt(user.email, success=False)
            return rate_limit_response(
                _('Too many verification attempts. Please try again later.')
            )
        
        # Record successful verification
        EmailVerificationRateLimiter.record_verification_attempt(user.email, success=True)
        SecurityAuditLogger.log_verification_success(user, client_ip)
        
        # Log the user in after successful verification
        from django.contrib.auth import get_backends
        backend = get_backends()[0]
        user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
        login(request, user)
        messages.success(request, _('Your email has been verified successfully! Welcome to Linguify.'))
        return redirect('saas_web:dashboard')
    else:
        error = result['error']
        
        # For security, don't reveal which specific emails exist in failed attempts
        # Just record the attempt with a generic identifier
        if error in ['token_expired', 'token_used', 'invalid_token']:
            # Try to get user email from token if possible for logging
            try:
                from ..models.models import EmailVerificationToken
                token_obj = EmailVerificationToken.objects.get(token=token)
                EmailVerificationRateLimiter.record_verification_attempt(token_obj.user.email, success=False)
            except EmailVerificationToken.DoesNotExist:
                # Record attempt with IP only for invalid tokens
                EmailVerificationRateLimiter.record_verification_attempt(f"ip:{client_ip}", success=False)
        
        if error == 'token_expired':
            messages.error(request, _('This verification link has expired. Please request a new one.'))
        elif error == 'token_used':
            messages.error(request, _('This verification link has already been used.'))
        elif error == 'invalid_token':
            messages.error(request, _('This verification link is invalid.'))
        else:
            messages.error(request, _('An error occurred during verification. Please try again.'))
        
        return render(request, 'authentication/emails/email_verification_error.html', {
            'error': error
        })


def resend_verification_email_view(request):
    """View to resend verification email"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        client_ip = EmailVerificationRateLimiter.get_client_ip(request)
        
        # Basic input validation
        if not email or '@' not in email or len(email) > 254:
            messages.error(request, _('Please provide a valid email address.'))
            return redirect(request.META.get('HTTP_REFERER', '/auth/register/'))
        
        # Check rate limits
        allowed, remaining, reset_time = EmailVerificationRateLimiter.check_resend_attempts(email, client_ip)
        
        if not allowed:
            return rate_limit_response(
                _('Too many email resend attempts. Please wait before trying again.')
            )
        
        # Record the resend attempt
        EmailVerificationRateLimiter.record_resend_attempt(email)
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(email=email, is_active=False)
            
            result = EmailVerificationService.resend_verification_email(user, request)
            if result['success']:
                messages.success(request, _('Verification email sent successfully. Please check your inbox.'))
            else:
                if result['error'] == 'already_verified':
                    messages.info(request, _('This email is already verified.'))
                else:
                    messages.error(request, _('Failed to send verification email. Please try again.'))
                    
        except User.DoesNotExist:
            # Don't reveal whether email exists or not for security
            messages.success(request, _('If an unverified account exists with this email, a verification email has been sent.'))
        except Exception as e:
            messages.error(request, _('An error occurred. Please try again.'))
    else:
        messages.error(request, _('Invalid request method.'))
    
    return redirect(request.META.get('HTTP_REFERER', '/auth/register/'))