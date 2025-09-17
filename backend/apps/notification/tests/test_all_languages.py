#!/usr/bin/env python
"""
Script pour envoyer les emails de test dans toutes les langues
"""
import os
import sys
import django

# Remonter au répertoire backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.notification.services import send_terms_acceptance_email_and_notification

User = get_user_model()

def send_all_language_emails():
    """Envoie les emails dans toutes les langues supportées"""

    try:
        test_email = os.getenv('TEST_EMAIL')
        user = User.objects.get(email=test_email)
        print(f"✓ Utilisateur trouvé : {user.username} ({user.email})")
        original_language = user.interface_language
    except User.DoesNotExist:
        print(f"❌ Utilisateur {test_email} non trouvé")
        return False

    languages = [
        ('en', 'English', '🇬🇧'),
        ('fr', 'Français', '🇫🇷'),
        ('nl', 'Nederlands', '🇳🇱'),
        ('es', 'Español', '🇪🇸')
    ]

    print("\n" + "=" * 70)
    print("📧 ENVOI DES EMAILS DANS TOUTES LES LANGUES")
    print("=" * 70)
    test_email = os.getenv('TEST_EMAIL')
    print(f"Destination: {test_email}")
    print(f"Template: Nouveau design Linguify avec gradient et compatibilité email")
    print()

    success_count = 0
    for lang_code, lang_name, flag in languages:
        print(f"\n{flag} Envoi en {lang_name} ({lang_code.upper()})")
        print("-" * 40)

        # Changer la langue de l'utilisateur
        user.interface_language = lang_code
        user.save()

        # Envoyer l'email
        try:
            success = send_terms_acceptance_email_and_notification(user)
            if success:
                print(f"  ✅ Email envoyé avec succès")
                success_count += 1

                # Afficher les traductions clés
                if lang_code == 'en':
                    print(f"  📝 Titre: Action Required: Accept Terms of Use")
                    print(f"  🔘 Bouton: Review and Accept Terms")
                elif lang_code == 'fr':
                    print(f"  📝 Titre: Action requise : Accepter les Conditions d'Utilisation")
                    print(f"  🔘 Bouton: Consulter et Accepter les Conditions")
                elif lang_code == 'nl':
                    print(f"  📝 Titre: Actie vereist: Accepteer de Gebruiksvoorwaarden")
                    print(f"  🔘 Bouton: Bekijk en Accepteer Voorwaarden")
                elif lang_code == 'es':
                    print(f"  📝 Titre: Acción requerida: Aceptar los Términos de Uso")
                    print(f"  🔘 Bouton: Revisar y Aceptar Términos")
            else:
                print(f"  ❌ Échec de l'envoi")
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")

    # Restaurer la langue originale
    user.interface_language = original_language
    user.save()
    print(f"\n🔄 Langue utilisateur restaurée: {original_language}")

    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    print(f"✅ {success_count}/4 emails envoyés avec succès")
    print("\n🎨 Design appliqué:")
    print("  • Header: Gradient Linguify (#2D5BBA → #017E84)")
    print("  • Logo: Badge 'Open Linguify' sur fond blanc")
    print("  • Bouton: Fond bleu avec fallback solide pour Outlook")
    print("  • Layout: Table-based pour compatibilité maximale")
    print(f"\n📧 Vérifiez {test_email} pour voir les 4 versions")

    return success_count == 4

if __name__ == "__main__":
    print("🚀 Open Linguify - Test Emails Multilingues")
    print("=" * 70)

    success = send_all_language_emails()

    if success:
        print("\n✨ Tous les emails ont été envoyés avec succès!")
    else:
        print("\n⚠️ Certains emails n'ont pas pu être envoyés")
        sys.exit(1)