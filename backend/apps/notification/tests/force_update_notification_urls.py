#!/usr/bin/env python
"""
Script pour forcer la mise à jour des URLs de notifications vers la nouvelle page d'acceptation
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
from apps.notification.models import Notification

User = get_user_model()

def force_update_notification_urls():
    """Force la mise à jour des URLs de notifications vers la nouvelle page d'acceptation"""

    print("🔧 MISE À JOUR FORCÉE DES URLs DE NOTIFICATION")
    print("=" * 70)

    # Nouvelle URL d'acceptation
    backend_url = getattr(settings, 'SITE_URL', 'http://localhost:8081')
    new_terms_url = f"{backend_url}/authentication/terms/accept/"

    # Récupérer toutes les notifications de type terms/action_required
    notifications = Notification.objects.filter(
        type__in=['terms', 'terms_update', 'action_required']
    )

    updated_count = 0
    old_portal_count = 0

    print(f"📋 Traitement de {notifications.count()} notifications...")
    print(f"🎯 Nouvelle URL: {new_terms_url}")
    print("-" * 50)

    for notif in notifications:
        # Vérifier si la notification concerne les conditions d'utilisation
        is_terms = False
        if notif.message and ('terms' in notif.message.lower() or
                             'conditions' in notif.message.lower()):
            is_terms = True
        if notif.title and ('terms' in notif.title.lower() or
                           'conditions' in notif.title.lower()):
            is_terms = True

        if is_terms:
            # Initialiser data si nécessaire
            if not notif.data:
                notif.data = {}

            # Vérifier l'URL actuelle
            current_url = notif.data.get('action_url', '')

            # Si l'URL pointe vers le portal (ancien), la mettre à jour
            if 'localhost:8080' in current_url or 'openlinguify.com' in current_url:
                old_portal_count += 1
                notif.data['action_url'] = new_terms_url

                # Conserver les autres données existantes
                if 'action' not in notif.data:
                    notif.data['action'] = 'accept_terms'

                notif.save()
                updated_count += 1
                print(f"✅ {str(notif.id)[:8]}... - URL mise à jour: {current_url} → {new_terms_url}")

            elif current_url == new_terms_url:
                print(f"✓ {str(notif.id)[:8]}... - URL déjà correcte")

            elif not current_url:
                # Ajouter l'URL si elle n'existe pas
                notif.data['action_url'] = new_terms_url
                if 'action' not in notif.data:
                    notif.data['action'] = 'accept_terms'
                notif.save()
                updated_count += 1
                print(f"➕ {str(notif.id)[:8]}... - URL ajoutée: {new_terms_url}")

            else:
                print(f"⚠️ {str(notif.id)[:8]}... - URL non reconnue: {current_url}")

    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DE LA MISE À JOUR")
    print("=" * 70)
    print(f"• Notifications mises à jour: {updated_count}")
    print(f"• Anciennes URLs portal trouvées: {old_portal_count}")
    print(f"• Total traité: {notifications.count()}")

    # Afficher quelques exemples de notifications mises à jour
    if updated_count > 0:
        print("\n📋 Exemples de notifications mises à jour:")
        examples = Notification.objects.filter(
            type__in=['terms', 'terms_update', 'action_required'],
            data__action_url=new_terms_url
        ).order_by('-created_at')[:3]

        for ex in examples:
            print(f"\n• ID: {str(ex.id)[:8]}...")
            print(f"  Titre: {ex.title[:50]}")
            print(f"  URL: {ex.data.get('action_url', 'NO URL')}")
            print(f"  Utilisateur: {ex.user.email}")

    return updated_count

def reset_user_terms_status():
    """Remet l'utilisateur de test en statut non-accepté pour tester"""

    print("\n🔄 RÉINITIALISATION STATUT UTILISATEUR TEST")
    print("=" * 70)

    try:
        user = User.objects.get(email=os.getenv('TEST_EMAIL'))

        # Sauvegarder l'état actuel
        original_accepted = user.terms_accepted

        # Réinitialiser pour le test
        user.terms_accepted = False
        user.terms_accepted_at = None
        user.terms_version = None
        user.save()

        print(f"✓ Utilisateur: {user.email}")
        print(f"  • Avant: terms_accepted = {original_accepted}")
        print(f"  • Après: terms_accepted = {user.terms_accepted}")
        print(f"  • Prêt pour test d'acceptation")

        return True

    except User.DoesNotExist:
        print(f"⚠️ Utilisateur {os.getenv("TEST_EMAIL")} non trouvé")
        return False

if __name__ == "__main__":
    print("🚀 Open Linguify - Mise à Jour Forcée des URLs")
    print("=" * 70)

    # Mettre à jour les URLs de notification
    updated = force_update_notification_urls()

    # Réinitialiser le statut utilisateur pour le test
    user_reset = reset_user_terms_status()

    print("\n" + "=" * 70)
    print("✨ SYSTÈME PRÊT POUR TEST")
    print("=" * 70)
    print("\n🎯 Instructions de test:")
    print(f"1. Connectez-vous avec {os.getenv("TEST_EMAIL")}")
    print("2. Cliquez sur une notification de conditions")
    print("3. Vous devriez voir la nouvelle page d'acceptation")
    print("4. Cochez la case et cliquez sur 'Accepter'")
    print("5. Vérifiez que le statut est mis à jour dans la DB")

    if updated > 0:
        print(f"\n✅ {updated} notification(s) mise(s) à jour avec succès!")
    else:
        print("\n✅ Toutes les URLs étaient déjà correctes!")

    if user_reset:
        print("✅ Utilisateur de test réinitialisé!")
    else:
        print("⚠️ Problème avec l'utilisateur de test")