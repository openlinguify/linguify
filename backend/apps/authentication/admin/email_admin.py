# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from ..models.email_models import (
    EmailTemplate,
    EmailTemplateTranslation,
    EmailCampaign,
    EmailLog
)


class EmailTemplateTranslationInline(admin.TabularInline):
    """Inline pour gérer les traductions d'un template"""
    model = EmailTemplateTranslation
    extra = 1
    fields = ['language', 'subject', 'body_text', 'body_html']

    def get_extra(self, request, obj=None, **kwargs):
        """Ajouter une ligne vide seulement s'il n'y a pas de traductions"""
        if obj and obj.translations.exists():
            return 0
        return 1


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """Admin pour les templates d'email"""
    list_display = ['name', 'email_type', 'is_active', 'translation_count', 'created_at', 'updated_at']
    list_filter = ['email_type', 'is_active', 'created_at']
    search_fields = ['name']
    inlines = [EmailTemplateTranslationInline]
    ordering = ['-created_at']

    def translation_count(self, obj):
        """Afficher le nombre de traductions"""
        count = obj.translations.count()
        return format_html(
            '<span style="color: {};">{} traduction(s)</span>',
            'green' if count >= 4 else 'orange' if count > 0 else 'red',
            count
        )
    translation_count.short_description = _('Translations')


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    """Admin pour les campagnes d'email"""
    list_display = [
        'name', 'template', 'recipient_type', 'status_colored',
        'total_recipients', 'sent_count', 'failed_count',
        'scheduled_at', 'sent_at', 'created_by'
    ]
    list_filter = ['status', 'recipient_type', 'created_at', 'sent_at']
    search_fields = ['name', 'template__name']
    readonly_fields = [
        'status', 'sent_at', 'total_recipients',
        'sent_count', 'failed_count', 'created_by',
        'created_at', 'updated_at'
    ]
    fieldsets = (
        (_('Campaign Information'), {
            'fields': ('name', 'template', 'status')
        }),
        (_('Recipients'), {
            'fields': ('recipient_type', 'custom_recipients', 'total_recipients')
        }),
        (_('Testing'), {
            'fields': ('test_email',),
            'description': _('Send a test email before launching the campaign')
        }),
        (_('Scheduling'), {
            'fields': ('scheduled_at',)
        }),
        (_('Template Variables'), {
            'fields': ('context_data',),
            'classes': ('collapse',),
            'description': _('JSON data to use as template variables (e.g., {"company_name": "MyCompany"})')
        }),
        (_('Statistics'), {
            'fields': ('sent_count', 'failed_count', 'sent_at'),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['send_test_email', 'send_campaign_action', 'duplicate_campaign']

    def save_model(self, request, obj, form, change):
        """Ajouter automatiquement l'utilisateur créateur"""
        if not change:  # Si c'est une création
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def status_colored(self, obj):
        """Afficher le statut avec des couleurs"""
        colors = {
            'draft': 'gray',
            'scheduled': 'blue',
            'sending': 'orange',
            'sent': 'green',
            'failed': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = _('Status')

    def send_test_email(self, request, queryset):
        """Action pour envoyer un email de test"""
        for campaign in queryset:
            if not campaign.test_email:
                messages.warning(
                    request,
                    f'Campaign "{campaign.name}" has no test email configured.'
                )
                continue

            success, message = campaign.send_test()
            if success:
                messages.success(
                    request,
                    f'Test email sent successfully for campaign "{campaign.name}"'
                )
            else:
                messages.error(
                    request,
                    f'Failed to send test email for campaign "{campaign.name}": {message}'
                )
    send_test_email.short_description = _('Send test email')

    def send_campaign_action(self, request, queryset):
        """Action pour envoyer les campagnes sélectionnées"""
        for campaign in queryset.filter(status__in=['draft', 'scheduled']):
            success, message = campaign.send_campaign()
            if success:
                messages.success(request, f'Campaign "{campaign.name}": {message}')
            else:
                messages.error(request, f'Campaign "{campaign.name}": {message}')
    send_campaign_action.short_description = _('Send campaign now')

    def duplicate_campaign(self, request, queryset):
        """Action pour dupliquer une campagne"""
        for campaign in queryset:
            # Créer une copie
            new_campaign = EmailCampaign.objects.create(
                name=f"{campaign.name} (Copy)",
                template=campaign.template,
                recipient_type=campaign.recipient_type,
                custom_recipients=campaign.custom_recipients,
                test_email=campaign.test_email,
                context_data=campaign.context_data,
                status='draft',
                created_by=request.user
            )
            messages.success(
                request,
                f'Campaign "{campaign.name}" duplicated successfully'
            )
    duplicate_campaign.short_description = _('Duplicate campaign')

    def get_urls(self):
        """Ajouter des URLs personnalisées"""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:campaign_id>/preview/',
                self.admin_site.admin_view(self.preview_campaign),
                name='authentication_emailcampaign_preview'
            ),
        ]
        return custom_urls + urls

    def preview_campaign(self, request, campaign_id):
        """Vue pour prévisualiser une campagne"""
        from django.shortcuts import render, get_object_or_404
        campaign = get_object_or_404(EmailCampaign, pk=campaign_id)

        # Obtenir toutes les traductions disponibles
        translations = campaign.template.translations.all()

        # Rendre avec le contexte de la campagne
        context_data = campaign.context_data or {}
        context_data['user'] = {
            'email': 'user@example.com',
            'username': 'example_user',
            'first_name': 'John',
            'last_name': 'Doe'
        }

        preview_data = []
        for trans in translations:
            preview_data.append({
                'language': trans.get_language_display(),
                'subject': trans.render_subject(context_data),
                'body_text': trans.render_body_text(context_data),
                'body_html': trans.render_body_html(context_data)
            })

        return render(request, 'admin/email_campaign_preview.html', {
            'campaign': campaign,
            'preview_data': preview_data,
            'opts': self.model._meta,
            'has_view_permission': True,
        })


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin pour les logs d'emails"""
    list_display = ['recipient', 'subject', 'campaign', 'status_colored', 'sent_at']
    list_filter = ['status', 'sent_at', 'campaign']
    search_fields = ['recipient', 'subject', 'campaign__name']
    readonly_fields = ['campaign', 'recipient', 'subject', 'status', 'error_message', 'sent_at']
    ordering = ['-sent_at']

    def status_colored(self, obj):
        """Afficher le statut avec des couleurs"""
        colors = {
            'sent': 'green',
            'failed': 'red',
            'bounced': 'orange'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = _('Status')

    def has_add_permission(self, request):
        """Désactiver l'ajout manuel de logs"""
        return False

    def has_change_permission(self, request, obj=None):
        """Logs en lecture seule"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Permettre la suppression pour le nettoyage"""
        return request.user.is_superuser