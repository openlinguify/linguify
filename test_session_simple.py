#!/usr/bin/env python
"""
Test simple pour vérifier le partage de session
Requires: Backend running on port 8081, Portal running on port 8080
"""
import requests

def test():
    print("=" * 60)
    print("BACKEND -> PORTAL SESSION DETECTION TEST (SIMPLE)")
    print("=" * 60)
    print("\nPrerequisites:")
    print("1. Backend running on http://127.0.0.1:8081")
    print("2. Portal running on http://127.0.0.1:8080")
    print()

    # 1. Créer une session de test
    print("Step 1: Creating test session...")
    import os
    import sys
    sys.path.insert(0, 'backend')
    os.chdir('backend')

    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

    from django.contrib.auth import get_user_model
    from django.contrib.sessions.backends.db import SessionStore

    User = get_user_model()
    admin = User.objects.filter(email='louisphilippelalou@outlook.com').first()

    if not admin:
        print("  FAIL: Admin user not found")
        return False

    # Créer session
    session = SessionStore()
    session['_auth_user_id'] = str(admin.id)
    session['_auth_user_backend'] = 'apps.authentication.backends.EmailOrUsernameModelBackend'
    session['_auth_user_hash'] = admin.get_session_auth_hash()
    session.save()

    print(f"  OK: Session created")
    print(f"  Session key: {session.session_key}")
    print(f"  User: {admin.username} ({admin.email})")

    os.chdir('..')

    # 2. Tester l'API backend
    print("\nStep 2: Testing backend API...")
    try:
        url = f"http://127.0.0.1:8081/api/auth/check-session/?session_key={session.session_key}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data.get('authenticated'):
                print(f"  OK: API works!")
                print(f"  User: {data['user']['username']}")
            else:
                print(f"  FAIL: Not authenticated - {data.get('error')}")
                return False
        else:
            print(f"  FAIL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  FAIL: {e}")
        print("  Make sure backend is running on port 8081")
        return False

    # 3. Tester le portal
    print("\nStep 3: Testing portal middleware...")
    try:
        cookies = {'sessionid': session.session_key}
        response = requests.get(
            "http://127.0.0.1:8080/test/backend-session/",
            cookies=cookies,
            timeout=5
        )

        if response.status_code == 200:
            if 'Backend User Detected!' in response.text:
                print("  OK: Portal detects backend user!")
            else:
                print("  FAIL: Portal doesn't detect user")
                print("  Visit http://127.0.0.1:8080/test/backend-session/ to debug")
                return False
        else:
            print(f"  FAIL: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"  FAIL: {e}")
        print("  Make sure portal is running on port 8080")
        return False

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("\nManual test:")
    print("1. Go to http://127.0.0.1:8081/en/auth/login/")
    print("2. Login: louisphilippelalou@outlook.com / Chon@728596")
    print("3. Go to http://127.0.0.1:8080/")
    print("4. Header should show your profile!")

    return True

if __name__ == "__main__":
    import sys
    success = test()
    sys.exit(0 if success else 1)
