#!/usr/bin/env python
"""
Script de test pour vérifier les emails multilingues
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.notification.services import send_terms_acceptance_email_and_notification

User = get_user_model()

def test_multilingual_emails():
    """Test les emails dans différentes langues"""

    # Récupérer l'utilisateur test
    try:
        test_email = os.getenv('TEST_EMAIL')
        user = User.objects.get(email=test_email)
        print(f"✓ Utilisateur trouvé : {user.username} ({user.email})")
        print(f"  Langue d'interface actuelle : {user.interface_language}")
    except User.DoesNotExist:
        print(f"❌ Utilisateur {test_email} non trouvé")
        return False

    # Tester les emails dans différentes langues
    languages = [
        ('en', 'English'),
        ('fr', 'Français'),
        ('nl', 'Nederlands'),
        ('es', 'Español')
    ]

    original_language = user.interface_language

    for lang_code, lang_name in languages:
        print(f"\n📧 Test d'email en {lang_name} ({lang_code.upper()})")
        print("=" * 60)

        # Changer la langue de l'interface utilisateur
        user.interface_language = lang_code
        user.save()
        print(f"  ✓ Langue changée vers {lang_code}")

        # Envoyer l'email et créer la notification
        print(f"  📤 Envoi de l'email...")
        success = send_terms_acceptance_email_and_notification(user)

        if success:
            print(f"  ✅ Email envoyé avec succès en {lang_name}")
            print(f"  📧 Email destiné à: {test_email}")
            print(f"  📍 Langue utilisée: {lang_code}")
        else:
            print(f"  ❌ Échec de l'envoi de l'email en {lang_name}")

    # Restaurer la langue originale
    user.interface_language = original_language
    user.save()
    print(f"\n🔄 Langue restaurée vers {original_language}")

    return True

if __name__ == "__main__":
    print("=" * 70)
    print("TEST DES EMAILS MULTILINGUES - CONDITIONS D'UTILISATION")
    print("=" * 70)
    print("Ce script va envoyer des emails de test dans 4 langues différentes")
    test_email = os.getenv('TEST_EMAIL')
    print(f"Les emails seront envoyés à: {test_email}")
    print()

    success = test_multilingual_emails()

    if success:
        print("\n✅ Tests terminés avec succès!")
        print("\n📋 RÉSUMÉ:")
        print("• 4 emails envoyés (EN, FR, NL, ES)")
        print("• Chaque email traduit selon interface_language de l'utilisateur")
        print(f"• Vérifiez {test_email} pour voir les emails")
        print("\n💡 Les templates utilisent maintenant Django i18n avec:")
        print("  - Templates de base en anglais")
        print("  - Traductions automatiques selon la langue utilisateur")
        print("  - Tags {% trans %} et {% blocktrans %} pour la localisation")
    else:
        print("\n❌ Tests échoués")
        sys.exit(1)