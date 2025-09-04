#!/usr/bin/env python
"""
Script pour créer un superuser pour le CMS Django
Utilisation: python create_superuser.py [username] [email] [password]
"""

import os
import sys
import django

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings')
django.setup()

from django.contrib.auth.models import User


def create_superuser(username='admin', email='admin@linguify.com', password='admin123', 
                    first_name='Admin', last_name='Teacher'):
    """
    Crée un superuser pour le CMS.
    
    Args:
        username (str): Nom d'utilisateur
        email (str): Email du superuser
        password (str): Mot de passe
        first_name (str): Prénom
        last_name (str): Nom de famille
    """
    try:
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            print(f"⚠️  Un utilisateur '{username}' existe déjà")
            user = User.objects.get(username=username)
            
            # Mettre à jour les informations si nécessaire
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            
            print(f"✅ Informations mises à jour pour '{username}'")
        else:
            # Créer un nouveau superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            print(f"✅ Superuser '{username}' créé avec succès !")
        
        # Afficher les informations d'accès
        print("\n" + "=" * 50)
        print("📋 INFORMATIONS D'ACCÈS CMS")
        print("=" * 50)
        print(f"URL Admin: http://localhost:8000/admin/")
        print(f"URL Teachers: http://localhost:8000/teachers/")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Password: {password}")
        print(f"Superuser: {'✅' if user.is_superuser else '❌'}")
        print(f"Staff: {'✅' if user.is_staff else '❌'}")
        print(f"Active: {'✅' if user.is_active else '❌'}")
        print("=" * 50)
        
        return user
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du superuser: {e}")
        return None


def create_teacher_user(username, email, password, first_name='', last_name=''):
    """
    Crée un utilisateur professeur (non-superuser).
    
    Args:
        username (str): Nom d'utilisateur
        email (str): Email
        password (str): Mot de passe
        first_name (str): Prénom
        last_name (str): Nom de famille
    """
    from apps.teachers.models import Teacher
    
    try:
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            print(f"⚠️  Un utilisateur '{username}' existe déjà")
            return None
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Créer le profil professeur
        teacher = Teacher.objects.create(
            user=user,
            status=Teacher.Status.APPROVED,
            hourly_rate=30.00,
            bio_en=f"Hello, I'm {first_name or username}!",
            bio_fr=f"Bonjour, je suis {first_name or username} !",
        )
        
        print(f"✅ Professeur '{username}' créé avec succès !")
        print(f"   User ID: {user.id}")
        print(f"   Teacher ID: {teacher.id}")
        
        return user, teacher
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du professeur: {e}")
        return None


def main():
    """Fonction principale."""
    if len(sys.argv) > 1:
        username = sys.argv[1]
        email = sys.argv[2] if len(sys.argv) > 2 else f"{username}@linguify.com"
        password = sys.argv[3] if len(sys.argv) > 3 else "password123"
        
        print(f"Création du superuser '{username}'...")
        create_superuser(username, email, password)
    else:
        print("Création du superuser par défaut...")
        create_superuser()
        
        print("\n" + "=" * 50)
        print("💡 CRÉER D'AUTRES UTILISATEURS")
        print("=" * 50)
        print("Superuser personnalisé:")
        print("  python create_superuser.py [username] [email] [password]")
        print()
        print("Créer un professeur de test:")
        print("  python -c \"from create_superuser import create_teacher_user; create_teacher_user('prof1', 'prof1@linguify.com', 'prof123', 'Marie', 'Dupont')\"")


if __name__ == "__main__":
    main()