#!/usr/bin/env python
"""
Script pour corriger les notifications existantes en ajoutant l'URL d'action
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

def fix_existing_notifications():
    """Corrige les notifications existantes en ajoutant action_url"""

    print("🔧 CORRECTION DES NOTIFICATIONS EXISTANTES")
    print("=" * 70)

    # Récupérer toutes les notifications de type terms/action_required
    notifications = Notification.objects.filter(
        type__in=['terms', 'terms_update', 'action_required']
    )

    backend_url = getattr(settings, 'SITE_URL', 'http://localhost:8081')
    terms_url = f"{backend_url}/authentication/terms/accept/"

    fixed_count = 0
    already_ok = 0

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

            # Vérifier si action_url existe déjà
            if 'action_url' in notif.data:
                already_ok += 1
                print(f"✓ {str(notif.id)[:8]}... - URL déjà présente")
            else:
                # Ajouter action_url
                notif.data['action_url'] = terms_url

                # Conserver les autres données existantes
                if 'terms_url' in notif.data:
                    # Remplacer terms_url par action_url
                    del notif.data['terms_url']

                # Ajouter action si pas présent
                if 'action' not in notif.data:
                    notif.data['action'] = 'accept_terms'

                notif.save()
                fixed_count += 1
                print(f"✅ {str(notif.id)[:8]}... - URL ajoutée: {terms_url}")

    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    print(f"• Notifications corrigées: {fixed_count}")
    print(f"• Déjà correctes: {already_ok}")
    print(f"• Total traité: {fixed_count + already_ok}")

    # Afficher quelques exemples
    if fixed_count > 0:
        print("\n📋 Exemples de notifications corrigées:")
        examples = Notification.objects.filter(
            type__in=['terms', 'terms_update', 'action_required'],
            data__action_url__isnull=False
        ).order_by('-created_at')[:3]

        for ex in examples:
            print(f"\n• ID: {str(ex.id)[:8]}...")
            print(f"  Titre: {ex.title[:50]}")
            if ex.data and 'action_url' in ex.data:
                print(f"  URL: {ex.data['action_url']}")

    return fixed_count

def reset_unread_terms_notifications():
    """Marque les notifications de conditions comme non lues pour test"""

    print("\n🔄 RÉINITIALISATION DES NOTIFICATIONS NON LUES")
    print("=" * 70)

    # Pour l'utilisateur de test
    try:
        user = User.objects.get(email=os.getenv('TEST_EMAIL'))

        # Marquer les dernières notifications terms comme non lues
        notifications = Notification.objects.filter(
            user=user,
            type__in=['terms', 'terms_update', 'action_required']
        ).order_by('-created_at')[:2]  # Les 2 dernières

        reset_count = 0
        for notif in notifications:
            if notif.is_read:
                notif.is_read = False
                notif.save()
                reset_count += 1
                print(f"🔵 Marquée non lue: {notif.title[:50]}")

        if reset_count > 0:
            print(f"\n✅ {reset_count} notification(s) marquée(s) comme non lue(s)")
        else:
            print("ℹ️ Toutes les notifications sont déjà non lues")

    except User.DoesNotExist:
        print(f"⚠️ Utilisateur {os.getenv("TEST_EMAIL")} non trouvé")

if __name__ == "__main__":
    print("🚀 Open Linguify - Correction des Notifications")
    print("=" * 70)

    # Corriger les notifications existantes
    fixed = fix_existing_notifications()

    # Réinitialiser quelques notifications pour test
    reset_unread_terms_notifications()

    print("\n" + "=" * 70)
    print("✨ TERMINÉ")
    print("=" * 70)
    print("\n📱 Pour tester:")
    print(f"1. Connectez-vous avec {os.getenv("TEST_EMAIL")}")
    print("2. Cliquez sur une notification de conditions d'utilisation")
    print("3. Vous devriez être redirigé vers les terms")

    if fixed > 0:
        print(f"\n✅ {fixed} notifications corrigées avec succès!")
    else:
        print("\n✅ Toutes les notifications étaient déjà correctes!")