# Generated manually for cookie consent models

import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0016_alter_user_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='CookieConsent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_id', models.CharField(blank=True, help_text='Session ID for anonymous users', max_length=40, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='IP address when consent was given', null=True)),
                ('user_agent', models.TextField(blank=True, help_text='User agent string when consent was given', null=True)),
                ('version', models.CharField(default='1.0', help_text='Version of the consent form', max_length=10)),
                ('essential', models.BooleanField(default=True, help_text='Essential cookies (always true)')),
                ('analytics', models.BooleanField(default=False, help_text='Analytics cookies (Google Analytics, etc.)')),
                ('functionality', models.BooleanField(default=False, help_text='Functionality cookies (user preferences, etc.)')),
                ('performance', models.BooleanField(default=False, help_text='Performance cookies (caching, optimization, etc.)')),
                ('language', models.CharField(default='fr', help_text='Language when consent was given', max_length=10)),
                ('consent_method', models.CharField(choices=[('banner', 'Cookie Banner'), ('settings', 'Settings Page'), ('api', 'API Call'), ('import', 'Data Import')], default='banner', help_text='How the consent was obtained', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When consent was given')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='When consent was last updated')),
                ('expires_at', models.DateTimeField(blank=True, help_text='When consent expires (null = never)', null=True)),
                ('is_revoked', models.BooleanField(default=False, help_text='Whether consent has been revoked')),
                ('revoked_at', models.DateTimeField(blank=True, help_text='When consent was revoked', null=True)),
                ('revocation_reason', models.CharField(blank=True, choices=[('user_request', 'User Request'), ('expired', 'Expired'), ('version_change', 'Version Change'), ('admin_action', 'Admin Action'), ('data_deletion', 'Account Deletion')], help_text='Reason for revocation', max_length=100, null=True)),
                ('user', models.ForeignKey(blank=True, help_text='User who gave consent (null for anonymous users)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cookie_consents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Cookie Consent',
                'verbose_name_plural': 'Cookie Consents',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CookieConsentLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('revoked', 'Revoked'), ('expired', 'Expired')], max_length=20)),
                ('old_values', models.JSONField(blank=True, help_text='Previous values before change', null=True)),
                ('new_values', models.JSONField(blank=True, help_text='New values after change', null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('consent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='authentication.cookieconsent')),
            ],
            options={
                'verbose_name': 'Cookie Consent Log',
                'verbose_name_plural': 'Cookie Consent Logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='cookieconsent',
            index=models.Index(fields=['user', '-created_at'], name='authenticat_user_id_f7d69f_idx'),
        ),
        migrations.AddIndex(
            model_name='cookieconsent',
            index=models.Index(fields=['session_id', '-created_at'], name='authenticat_session_4d86e3_idx'),
        ),
        migrations.AddIndex(
            model_name='cookieconsent',
            index=models.Index(fields=['ip_address', '-created_at'], name='authenticat_ip_addr_a91c3f_idx'),
        ),
        migrations.AddIndex(
            model_name='cookieconsent',
            index=models.Index(fields=['version'], name='authenticat_version_c4b0a9_idx'),
        ),
        migrations.AddIndex(
            model_name='cookieconsent',
            index=models.Index(fields=['created_at'], name='authenticat_created_4d1e0f_idx'),
        ),
        migrations.AddIndex(
            model_name='cookieconsent',
            index=models.Index(fields=['is_revoked'], name='authenticat_is_revo_dfe4d3_idx'),
        ),
        migrations.AddIndex(
            model_name='cookieconsentlog',
            index=models.Index(fields=['consent', '-created_at'], name='authenticat_consent_24b14e_idx'),
        ),
        migrations.AddIndex(
            model_name='cookieconsentlog',
            index=models.Index(fields=['action'], name='authenticat_action_85bb12_idx'),
        ),
        migrations.AddIndex(
            model_name='cookieconsentlog',
            index=models.Index(fields=['created_at'], name='authenticat_created_19b2ad_idx'),
        ),
        migrations.AddConstraint(
            model_name='cookieconsent',
            constraint=models.UniqueConstraint(condition=models.Q(('is_revoked', False), ('user__isnull', False)), fields=('user',), name='unique_active_user_consent'),
        ),
    ]