#!/usr/bin/env python
"""
Script de test rapide pour vérifier le layout email corrigé
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

def test_email_layout():
    """Test l'email avec le layout corrigé"""

    try:
        test_email = os.getenv('TEST_EMAIL')
        user = User.objects.get(email=test_email)
        print(f"✓ Utilisateur trouvé : {user.username}")
    except User.DoesNotExist:
        print("❌ Utilisateur non trouvé")
        return False

    # Test en français (pour voir les corrections)
    user.interface_language = 'fr'
    user.save()

    print("📧 Envoi d'un email de test avec layout corrigé...")
    success = send_terms_acceptance_email_and_notification(user)

    if success:
        print("✅ Email envoyé avec succès !")
        print("📋 Corrections appliquées :")
        print("  • Bouton CTA : fond bleu solide (#2D5BBA) avec !important")
        print("  • Texte bouton : blanc avec !important")
        print("  • Header : fond bleu solide (pas de gradient)")
        print("  • Logo : amélioré avec inline-block et line-height")
        print("  • Body : fond uni (pas de gradient)")
        print(f"\n📧 Vérifiez {test_email} pour voir les améliorations")
    else:
        print("❌ Échec de l'envoi")

    return success

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU LAYOUT EMAIL CORRIGÉ")
    print("=" * 60)

    success = test_email_layout()

    if success:
        print("\n🎉 Test terminé ! Le layout devrait maintenant être correct.")
    else:
        print("\n💥 Test échoué")
        sys.exit(1)