# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.
from django.db import models
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.mail import send_mass_mail, send_mail
from django.template import Template, Context
from django.utils import timezone
import json

User = get_user_model()

class EmailTemplate(models.Model):
    """Template d'email multilingue"""
    EMAIL_TYPES = [
        ('announcement', _('General Announcement')),
        ('feature', _('New Feature Announcement')),
        ('survey', _('Survey')),
        ('feedback', _('Feedback Request')),
        ('maintenance', _('Maintenance Notice')),
        ('newsletter', _('Newsletter')),
    ]

    name = models.CharField(max_length=100, verbose_name=_('Template Name'))
    email_type = models.CharField(max_length=20, choices=EMAIL_TYPES, verbose_name=_('Email Type'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Email Template")
        verbose_name_plural = _("Email Templates")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_email_type_display()})"

class EmailTemplateTranslation(models.Model):
    """Traductions pour les templates d'email"""
    LANGUAGE_CHOICES = [
        ('fr', _('French')),
        ('en', _('English')),
        ('es', _('Spanish')),
        ('nl', _('Dutch')),
    ]

    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, verbose_name=_('Language'))
    subject = models.CharField(max_length=200, verbose_name=_('Subject'))
    body_text = models.TextField(verbose_name=_('Body (Text)'), help_text=_('Plain text version'))
    body_html = models.TextField(verbose_name=_('Body (HTML)'), blank=True, help_text=_('HTML version (optional)'))

    class Meta:
        verbose_name = _("Email Translation")
        verbose_name_plural = _("Email Translations")
        unique_together = ['template', 'language']
        ordering = ['language']

    def __str__(self):
        return f"{self.template.name} - {self.get_language_display()}"

    def render_subject(self, context=None):
        """Rendre le sujet avec le contexte"""
        if context:
            template = Template(self.subject)
            return template.render(Context(context))
        return self.subject

    def render_body_text(self, context=None):
        """Rendre le corps text avec le contexte"""
        if context:
            template = Template(self.body_text)
            return template.render(Context(context))
        return self.body_text

    def render_body_html(self, context=None):
        """Rendre le corps HTML avec le contexte"""
        if self.body_html:
            if context:
                template = Template(self.body_html)
                return template.render(Context(context))
            return self.body_html
        return None

class EmailCampaign(models.Model):
    """Campagne d'envoi d'emails depuis l'admin"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('scheduled', _('Scheduled')),
        ('sending', _('Sending')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
    ]

    RECIPIENT_CHOICES = [
        ('all', _('All Users')),
        ('active', _('Active Users Only')),
        ('premium', _('Premium Users')),
        ('selected', _('Selected Users')),
        ('custom', _('Custom List')),
    ]

    name = models.CharField(max_length=100, verbose_name=_('Campaign Name'))
    template = models.ForeignKey(EmailTemplate, on_delete=models.PROTECT, verbose_name=_('Email Template'))
    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_CHOICES, default='all', verbose_name=_('Recipients'))
    selected_users = models.ManyToManyField(User, blank=True, related_name='email_campaigns_received', verbose_name=_('Selected Users'))
    custom_recipients = models.TextField(blank=True, help_text=_('Email addresses separated by commas (for custom list)'))
    test_email = models.EmailField(blank=True, help_text=_('Send test email to this address before campaign'))

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_('Status'))
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Schedule Send'))
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Sent At'))

    total_recipients = models.IntegerField(default=0, verbose_name=_('Total Recipients'))
    sent_count = models.IntegerField(default=0, verbose_name=_('Emails Sent'))
    failed_count = models.IntegerField(default=0, verbose_name=_('Failed Emails'))

    context_data = models.JSONField(default=dict, blank=True, help_text=_('JSON data for template variables'))

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='email_campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Email Campaign")
        verbose_name_plural = _("Email Campaigns")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"

    def get_recipients(self):
        """Obtenir la liste des destinataires selon le type"""
        if self.recipient_type == 'all':
            return User.objects.filter(is_active=True).values_list('email', flat=True)
        elif self.recipient_type == 'active':
            # À adapter selon votre logique d'utilisateurs actifs
            from datetime import timedelta
            cutoff = timezone.now() - timedelta(days=30)
            return User.objects.filter(
                is_active=True,
                last_login__gte=cutoff
            ).values_list('email', flat=True)
        elif self.recipient_type == 'premium':
            # À adapter selon votre logique d'utilisateurs premium
            return User.objects.filter(
                is_active=True,
                # subscription__is_premium=True  # Exemple
            ).values_list('email', flat=True)
        elif self.recipient_type == 'selected':
            return self.selected_users.filter(is_active=True).values_list('email', flat=True)
        elif self.recipient_type == 'custom':
            if self.custom_recipients:
                return [email.strip() for email in self.custom_recipients.split(',') if email.strip()]
        return []

    def send_test(self):
        """Envoyer un email de test"""
        if not self.test_email:
            return False, "No test email specified"

        try:
            # Obtenir la traduction en anglais par défaut
            translation = self.template.translations.filter(language='en').first()
            if not translation:
                translation = self.template.translations.first()

            if not translation:
                return False, "No translation found for template"

            context = self.context_data or {}
            context['is_test'] = True

            # Ajouter des données utilisateur de test
            context['user'] = {
                'email': self.test_email,
                'username': 'test_user',
                'first_name': 'Test',
                'last_name': 'User',
            }

            send_mail(
                subject=f"[TEST] {translation.render_subject(context)}",
                message=translation.render_body_text(context),
                html_message=translation.render_body_html(context),
                from_email=None,  # Utilisera DEFAULT_FROM_EMAIL
                recipient_list=[self.test_email],
                fail_silently=False,
            )
            return True, "Test email sent successfully"
        except Exception as e:
            return False, str(e)

    def send_campaign(self):
        """Envoyer la campagne d'emails"""
        if self.status != 'draft' and self.status != 'scheduled':
            return False, "Campaign is not in draft or scheduled status"

        recipients = list(self.get_recipients())
        if not recipients:
            return False, "No recipients found"

        self.status = 'sending'
        self.total_recipients = len(recipients)
        self.save()

        try:
            # Pour chaque langue, envoyer aux utilisateurs correspondants
            success_count = 0
            failed_count = 0

            for recipient in recipients:
                try:
                    user = User.objects.filter(email=recipient).first()
                    # Déterminer la langue de l'utilisateur
                    user_lang = 'en'  # Par défaut
                    if user and hasattr(user, 'language'):
                        user_lang = user.language

                    translation = self.template.translations.filter(language=user_lang).first()
                    if not translation:
                        translation = self.template.translations.filter(language='en').first()

                    if translation:
                        context = self.context_data or {}
                        if user:
                            context['user'] = {
                                'email': user.email,
                                'username': user.username,
                                'first_name': getattr(user, 'first_name', ''),
                                'last_name': getattr(user, 'last_name', ''),
                            }

                        send_mail(
                            subject=translation.render_subject(context),
                            message=translation.render_body_text(context),
                            html_message=translation.render_body_html(context),
                            from_email=None,
                            recipient_list=[recipient],
                            fail_silently=False,
                        )
                        success_count += 1
                except Exception:
                    failed_count += 1

            self.status = 'sent'
            self.sent_count = success_count
            self.failed_count = failed_count
            self.sent_at = timezone.now()
            self.save()

            return True, f"Campaign sent: {success_count} success, {failed_count} failed"

        except Exception as e:
            self.status = 'failed'
            self.save()
            return False, str(e)

class EmailLog(models.Model):
    """Journal des emails envoyés"""
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, related_name='logs', null=True, blank=True)
    recipient = models.EmailField(verbose_name=_('Recipient'))
    subject = models.CharField(max_length=200, verbose_name=_('Subject'))
    status = models.CharField(max_length=20, choices=[
        ('sent', _('Sent')),
        ('failed', _('Failed')),
        ('bounced', _('Bounced')),
    ], verbose_name=_('Status'))
    error_message = models.TextField(blank=True, verbose_name=_('Error Message'))
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sent At'))

    class Meta:
        verbose_name = _("Email Log")
        verbose_name_plural = _("Email Logs")
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.recipient} - {self.subject} - {self.get_status_display()}"
    