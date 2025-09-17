#!/usr/bin/env python
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
        user = User.objects.get(email=os.getenv('TEST_EMAIL'))
        print("📊 STATUT APRÈS ACCEPTATION")
        print("=" * 50)
        print(f"Email: {user.email}")
        print(f"Terms Accepted: {'✅ OUI' if user.terms_accepted else '❌ NON'}")
        print(f"Terms Accepted At: {user.terms_accepted_at or '❌ Non défini'}")
        print(f"Terms Version: {user.terms_version or '❌ Non défini'}")

        if user.terms_accepted:
            print("\n🎉 SUCCÈS! L'utilisateur a accepté les conditions")
        else:
            print("\n⚠️ L'utilisateur n'a pas encore accepté les conditions")

    except User.DoesNotExist:
        print("❌ Utilisateur non trouvé")

if __name__ == "__main__":
    check_acceptance()
