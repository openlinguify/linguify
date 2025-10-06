# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Envoie tous les types d\'emails de test à une adresse pour vérification'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='louisphilippelalou@outlook.com',
            help='Adresse email de destination pour les tests'
        )

    def handle(self, *args, **options):
        test_email = options['email']

        self.stdout.write(self.style.SUCCESS(f'\nEnvoi des emails de test a : {test_email}\n'))

        # 1. Email de vérification
        self.stdout.write('Envoi de l\'email de verification...')
        try:
            context = {
                'user': {
                    'first_name': 'Test',
                    'email': test_email
                },
                'verification_url': 'https://linguify.app/verify/test-token-123456',
            }

            html_content = render_to_string(
                'authentication/emails/email_verification.html',
                context
            )

            send_mail(
                subject='[TEST] Vérification de votre email - Linguify',
                message='Vérifiez votre email',
                html_message=html_content,
                from_email=None,
                recipient_list=[test_email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('OK - Email de verification envoye'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERREUR: {str(e)}'))

        # 2. Email de réinitialisation de mot de passe
        self.stdout.write('\nEnvoi de l\'email de reinitialisation de mot de passe...')
        try:
            context = {
                'protocol': 'https',
                'domain': 'linguify.app',
                'uid': 'test-uid',
                'token': 'test-token',
            }

            html_content = render_to_string(
                'authentication/password_reset/password_reset_email.html',
                context
            )

            send_mail(
                subject='[TEST] Réinitialisation de votre mot de passe - Linguify',
                message='Réinitialisez votre mot de passe',
                html_message=html_content,
                from_email=None,
                recipient_list=[test_email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('OK - Email de reinitialisation envoye'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERREUR: {str(e)}'))

        # 3. Email de rappel des conditions d'utilisation
        self.stdout.write('\nEnvoi de l\'email de rappel des conditions...')
        try:
            context = {
                'user': {
                    'first_name': 'Test',
                    'username': 'test_user',
                    'email': test_email
                },
                'app_name': 'Open Linguify',
                'terms_url': 'https://openlinguify.com/terms',
                'portal_url': 'https://openlinguify.com',
            }

            html_content = render_to_string(
                'emails/terms_reminder.html',
                context
            )

            send_mail(
                subject='[TEST] Action requise : Conditions d\'utilisation - Linguify',
                message='Acceptez les nouvelles conditions d\'utilisation',
                html_message=html_content,
                from_email=None,
                recipient_list=[test_email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('OK - Email de rappel des conditions envoye'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERREUR: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('\nTous les emails de test ont ete envoyes !'))
        self.stdout.write(self.style.WARNING('\nPour les templates de campagnes (annonce, newsletter, etc.),'))
        self.stdout.write(self.style.WARNING('creez-les dans l\'admin Django et utilisez le bouton "Send test email"'))
