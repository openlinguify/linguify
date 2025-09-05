#!/usr/bin/env python3
"""
Script de diagnostic pour les emails de réinitialisation de mot de passe
"""
import os
import django
from django.conf import settings

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
import traceback


def test_email_config():
    """Test de la configuration email"""
    print("=== CONFIGURATION EMAIL ===")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'NOT SET')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()


def test_smtp_connection():
    """Test de la connexion SMTP"""
    print("=== TEST CONNEXION SMTP ===")
    try:
        from django.core.mail import get_connection
        connection = get_connection()
        connection.open()
        print("✅ Connexion SMTP ouverte avec succès")
        connection.close()
        print("✅ Connexion SMTP fermée avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion SMTP: {e}")
        traceback.print_exc()
        return False


def test_simple_email(recipient_email):
    """Test d'envoi d'un email simple"""
    print("=== TEST EMAIL SIMPLE ===")
    try:
        result = send_mail(
            'Test Linguify - Email de diagnostic',
            'Ceci est un email de test pour vérifier la configuration email.',
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        print(f"✅ Email simple envoyé avec succès! Résultat: {result}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email simple: {e}")
        traceback.print_exc()
        return False


def test_password_reset_email(recipient_email):
    """Test d'envoi d'un email de réinitialisation de mot de passe"""
    print("=== TEST EMAIL RESET PASSWORD ===")
    try:
        User = get_user_model()
        
        # Vérifier si l'utilisateur existe
        try:
            user = User.objects.get(email=recipient_email)
            print(f"Utilisateur trouvé: {user.email} (Active: {user.is_active})")
        except User.DoesNotExist:
            print(f"❌ Utilisateur {recipient_email} non trouvé")
            return False
        
        # Utiliser le formulaire Django standard
        form = PasswordResetForm({'email': recipient_email})
        if form.is_valid():
            print("Formulaire valide, tentative d'envoi...")
            
            # Simuler une requête HTTP avec le domaine fonctionnel
            class MockRequest:
                def is_secure(self):
                    return True
                def get_host(self):
                    return 'linguify-h47a.onrender.com'
                META = {
                    'SERVER_NAME': 'linguify-h47a.onrender.com',
                    'SERVER_PORT': '443'
                }
            
            request = MockRequest()
            
            form.save(
                subject_template_name='authentication/password_reset/password_reset_subject.txt',
                email_template_name='authentication/password_reset/password_reset_email.txt',
                use_https=True,
                from_email=settings.DEFAULT_FROM_EMAIL,
                request=request,
                html_email_template_name='authentication/password_reset/password_reset_email.html'
            )
            
            print("✅ Email de réinitialisation envoyé avec succès!")
            return True
        else:
            print(f"❌ Formulaire invalide: {form.errors}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email de réinitialisation: {e}")
        traceback.print_exc()
        return False


def main():
    """Fonction principale de diagnostic"""
    print("🔍 DIAGNOSTIC EMAIL LINGUIFY")
    print("=" * 50)
    
    # Test 1: Configuration
    test_email_config()
    
    # Test 2: Connexion SMTP
    smtp_ok = test_smtp_connection()
    print()
    
    if not smtp_ok:
        print("❌ Connexion SMTP échouée. Vérifiez la configuration.")
        return
    
    # Test 3: Email simple
    test_email = "linguify.info@gmail.com"  # Changé pour utiliser linguify.info@gmail.com
    simple_ok = test_simple_email(test_email)
    print()
    
    if not simple_ok:
        print("❌ Envoi d'email simple échoué.")
        return
    
    # Test 4: Email de réinitialisation
    reset_ok = test_password_reset_email(test_email)
    print()
    
    if reset_ok:
        print("✅ TOUS LES TESTS SONT PASSÉS!")
        print("Si vous ne recevez pas l'email:")
        print("1. Vérifiez votre dossier spam")
        print("2. Attendez quelques minutes")
        print("3. Vérifiez que l'adresse email est correcte")
        print("4. Contactez votre fournisseur de messagerie")
    else:
        print("❌ Test d'email de réinitialisation échoué.")
    
    print("=" * 50)


if __name__ == "__main__":
    main()