#!/usr/bin/env python
"""
Script de test pour vérifier le partage de session Backend -> Portal
"""
import subprocess
import time
import requests
import sys
import signal

def start_server(port, directory, timeout=30):
    """Démarre un serveur Django"""
    print(f"  Starting server on port {port}...")
    proc = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"{port}", "--noreload"],
        cwd=directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Attendre que le serveur démarre
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://127.0.0.1:{port}/health/", timeout=1)
            if response.status_code == 200:
                print(f"  OK Server started on port {port}")
                return proc
        except:
            time.sleep(0.5)

    print(f"  FAIL Server failed to start on port {port}")
    proc.kill()
    return None

def create_test_session():
    """Crée une session de test sur le backend"""
    print("\n2. Creating test session...")

    import os
    import django
    os.chdir("backend")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

    from django.contrib.auth import get_user_model
    from django.contrib.sessions.backends.db import SessionStore

    User = get_user_model()
    admin = User.objects.filter(email='louisphilippelalou@outlook.com').first()

    if not admin:
        print("  FAIL Admin user not found")
        return None

    # Créer une session
    session = SessionStore()
    session['_auth_user_id'] = str(admin.id)
    session['_auth_user_backend'] = 'apps.authentication.backends.EmailOrUsernameModelBackend'
    session['_auth_user_hash'] = admin.get_session_auth_hash()
    session.save()

    print(f"  OK Session created for {admin.username}")
    print(f"  Session key: {session.session_key}")

    os.chdir("..")
    return session.session_key

def test_backend_api(session_key):
    """Teste l'API backend"""
    print("\n3. Testing backend API...")

    url = f"http://127.0.0.1:8000/api/auth/check-session/?session_key={session_key}"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('authenticated'):
                print(f"  OK API works! User: {data['user']['username']}")
                return True
            else:
                print(f"  FAIL API returned not authenticated: {data.get('error')}")
                return False
        else:
            print(f"  FAIL API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  FAIL API error: {e}")
        return False

def test_portal_middleware(session_key):
    """Teste le middleware du portal"""
    print("\n4. Testing portal middleware...")

    # Créer une requête avec le cookie de session
    cookies = {'sessionid': session_key}

    try:
        response = requests.get(
            "http://127.0.0.1:8080/test/backend-session/",
            cookies=cookies,
            timeout=5
        )

        if response.status_code == 200:
            if 'Backend User Detected!' in response.text:
                print("  OK Portal detects backend user!")
                return True
            else:
                print("  FAIL Portal doesn't detect backend user")
                print("  Check /test/backend-session/ page")
                return False
        else:
            print(f"  FAIL Portal returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  FAIL Portal error: {e}")
        return False

def main():
    backend_proc = None
    portal_proc = None

    try:
        print("=" * 60)
        print("BACKEND -> PORTAL SESSION DETECTION TEST")
        print("=" * 60)

        # 1. Démarrer les serveurs
        print("\n1. Starting servers...")
        backend_proc = start_server(8000, "backend")
        if not backend_proc:
            print("\nFAIL FAILED: Backend server didn't start")
            return False

        portal_proc = start_server(8080, "portal")
        if not portal_proc:
            print("\nFAIL FAILED: Portal server didn't start")
            return False

        time.sleep(2)

        # 2. Créer une session
        session_key = create_test_session()
        if not session_key:
            print("\nFAIL FAILED: Couldn't create test session")
            return False

        # 3. Tester l'API backend
        if not test_backend_api(session_key):
            print("\nFAIL FAILED: Backend API test failed")
            return False

        # 4. Tester le middleware portal
        if not test_portal_middleware(session_key):
            print("\nFAIL FAILED: Portal middleware test failed")
            return False

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nManual test:")
        print(f"1. Go to http://127.0.0.1:8000/en/auth/login/")
        print(f"2. Login with louisphilippelalou@outlook.com / Chon@728596")
        print(f"3. Go to http://127.0.0.1:8080/")
        print(f"4. Header should show your profile!")
        print("\nServers will keep running. Press Ctrl+C to stop.")

        # Garder les serveurs actifs
        backend_proc.wait()

        return True

    except KeyboardInterrupt:
        print("\n\nStopping servers...")
        return True
    finally:
        if backend_proc:
            backend_proc.kill()
        if portal_proc:
            portal_proc.kill()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
