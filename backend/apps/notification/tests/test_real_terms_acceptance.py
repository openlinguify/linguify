#!/usr/bin/env python
"""
Test final pour vérifier l'acceptation réelle des conditions d'utilisation
avec vérification du changement de statut dans la base de données
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
from django.conf import settings
from django.utils import timezone
from apps.notification.services import send_terms_acceptance_email_and_notification
from apps.notification.models import Notification

User = get_user_model()

def check_user_terms_status(user, label=""):
    """Vérifie le statut des conditions d'utilisation de l'utilisateur"""
    print(f"\n📊 STATUT UTILISATEUR {label}")
    print("-" * 50)
    print(f"  • Email: {user.email}")
    print(f"  • Username: {user.username}")
    print(f"  • Interface Language: {user.interface_language}")
    print(f"  • Terms Accepted: {'✅' if user.terms_accepted else '❌'}")

    if user.terms_accepted_at:
        print(f"  • Terms Accepted At: {user.terms_accepted_at.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"  • Terms Accepted At: ❌ Non défini")

    print(f"  • Terms Version: {user.terms_version or '❌ Non défini'}")
    print(f"  • Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '❌'}")
    print(f"  • Is Active: {'✅' if user.is_active else '❌'}")

def test_real_terms_acceptance():
    """Test complet d'acceptation des conditions d'utilisation"""

    print("🚀 TEST FINAL - ACCEPTATION RÉELLE DES CONDITIONS")
    print("=" * 70)

    # 1. Récupérer l'utilisateur
    try:
        user = User.objects.get(email='linguify.info@gmail.com')
        print(f"✓ Utilisateur trouvé: {user.username} ({user.email})")
    except User.DoesNotExist:
        print("❌ Utilisateur linguify.info@gmail.com non trouvé")
        return False

    # 2. Vérifier le statut AVANT
    check_user_terms_status(user, "AVANT")

    # 3. Simuler le fait que l'utilisateur n'a pas accepté les conditions
    print(f"\n🔄 RÉINITIALISATION DU STATUT (pour test)")
    print("-" * 50)

    original_terms_accepted = user.terms_accepted
    original_terms_accepted_at = user.terms_accepted_at
    original_terms_version = user.terms_version

    # Marquer comme non accepté pour le test
    user.terms_accepted = False
    user.terms_accepted_at = None
    user.terms_version = None
    user.save()

    print("✓ Statut réinitialisé (terms_accepted = False)")
    check_user_terms_status(user, "APRÈS RÉINITIALISATION")

    # 4. Envoyer une vraie notification
    print(f"\n📧 ENVOI NOTIFICATION RÉELLE")
    print("-" * 50)

    success = send_terms_acceptance_email_and_notification(user)

    if success:
        print("✅ Notification et email envoyés avec succès")

        # Récupérer la dernière notification
        latest_notification = Notification.objects.filter(
            user=user,
            type='action_required'
        ).order_by('-created_at').first()

        if latest_notification:
            print(f"\n📋 Notification créée:")
            print(f"  • ID: {str(latest_notification.id)[:8]}...")
            print(f"  • Titre: {latest_notification.title}")
            print(f"  • Message: {latest_notification.message[:60]}...")
            print(f"  • Non lue: {'✓' if not latest_notification.is_read else '✗'}")

            if latest_notification.data and 'action_url' in latest_notification.data:
                action_url = latest_notification.data['action_url']
                print(f"  • Action URL: {action_url}")

                # Vérifier que l'URL pointe vers le portal
                portal_url = getattr(settings, 'PORTAL_URL', 'http://localhost:8080')
                expected_url = f"{portal_url}/annexes/terms"

                backend_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
                expected_url_new = f"{backend_url}/authentication/terms/accept/"

                if action_url == expected_url_new:
                    print("  ✅ URL correcte vers la page d'acceptation")
                else:
                    print(f"  ⚠️ URL incorrecte. Attendu: {expected_url_new}")
            else:
                print("  ❌ Pas d'action_url dans les données")
    else:
        print("❌ Échec d'envoi de la notification")
        return False

    # 5. Instructions pour le test manuel
    print(f"\n🧪 ÉTAPES DE TEST MANUEL")
    print("=" * 70)
    print(f"\n1️⃣ CONNEXION:")
    print(f"   • URL: http://localhost:8000/")
    print(f"   • Email: {user.email}")
    print(f"   • Mot de passe: TestPassword123!")

    print(f"\n2️⃣ CLIQUER SUR LA NOTIFICATION:")
    print(f"   • Cliquez sur l'icône cloche 🔔")
    print(f"   • Cliquez sur: '{latest_notification.title if latest_notification else 'Notification des conditions'}'")
    backend_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    print(f"   • Vous devriez être redirigé vers: {backend_url}/authentication/terms/accept/")

    print(f"\n3️⃣ ACCEPTER LES CONDITIONS:")
    print(f"   • Sur la page des conditions, cliquez sur 'Accepter'")
    print(f"   • Cela devrait mettre à jour le statut dans la base de données")

    print(f"\n4️⃣ VÉRIFIER LE CHANGEMENT:")
    print(f"   • Utilisez la commande: python apps/notification/tests/check_user_acceptance_status.py")
    print(f"   • Ou vérifiez dans l'admin Django")

    # 6. Créer un script de vérification
    verification_script = f"""#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def check_acceptance():
    try:
        user = User.objects.get(email='linguify.info@gmail.com')
        print("📊 STATUT APRÈS ACCEPTATION")
        print("=" * 50)
        print(f"Email: {{user.email}}")
        print(f"Terms Accepted: {{'✅ OUI' if user.terms_accepted else '❌ NON'}}")
        print(f"Terms Accepted At: {{user.terms_accepted_at or '❌ Non défini'}}")
        print(f"Terms Version: {{user.terms_version or '❌ Non défini'}}")

        if user.terms_accepted:
            print("\\n🎉 SUCCÈS! L'utilisateur a accepté les conditions")
        else:
            print("\\n⚠️ L'utilisateur n'a pas encore accepté les conditions")

    except User.DoesNotExist:
        print("❌ Utilisateur non trouvé")

if __name__ == "__main__":
    check_acceptance()
"""

    with open('/mnt/c/Users/louis/WebstormProjects/linguify/backend/apps/notification/tests/check_user_acceptance_status.py', 'w') as f:
        f.write(verification_script)

    print(f"\n📝 Script de vérification créé: check_user_acceptance_status.py")

    # 7. Remettre le statut original (si c'était accepté avant)
    print(f"\n🔄 RESTAURATION DU STATUT ORIGINAL")
    print("-" * 50)

    user.terms_accepted = original_terms_accepted
    user.terms_accepted_at = original_terms_accepted_at
    user.terms_version = original_terms_version
    user.save()

    print("✓ Statut original restauré")
    check_user_terms_status(user, "FINAL (RESTAURÉ)")

    # 8. Résumé
    print(f"\n" + "=" * 70)
    print("📋 RÉSUMÉ DU TEST")
    print("=" * 70)
    print(f"\n✅ Actions réalisées:")
    print(f"  • Notification de conditions d'utilisation envoyée")
    print(f"  • Email envoyé à {user.email}")
    print(f"  • URL de redirection configurée: {portal_url}/annexes/terms")
    print(f"  • Script de vérification créé")

    print(f"\n🎯 Pour tester:")
    print(f"  1. Connectez-vous et cliquez sur la notification")
    print(f"  2. Acceptez les conditions sur la page du portal")
    print(f"  3. Vérifiez le changement avec: poetry run python apps/notification/tests/check_user_acceptance_status.py")

    return True

if __name__ == "__main__":
    print("🚀 Open Linguify - Test Acceptation Réelle des Conditions")
    print("=" * 70)

    success = test_real_terms_acceptance()

    if success:
        print("\n✨ Test préparé avec succès!")
        print("👆 Suivez les étapes ci-dessus pour tester l'acceptation complète")
    else:
        print("\n⚠️ Échec de préparation du test")
        sys.exit(1)