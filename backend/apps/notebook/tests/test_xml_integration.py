#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test pour l'intégration XML dans l'application notebook
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.notebook.utils.xml_parser import xml_parser, render_xml_view_as_html, get_xml_view_data
from apps.notebook.models import Note, NoteCategory
from apps.authentication.models import User


def test_xml_parser():
    """Test du parser XML"""
    print("🔍 Test du parser XML...")

    # Récupérer toutes les vues
    views = xml_parser.get_all_views()
    print(f"✅ Nombre de vues trouvées: {len(views)}")

    for view_id, view_data in views.items():
        print(f"  - Vue: {view_id}")
        print(f"    Nom: {view_data.get('name', 'N/A')}")
        print(f"    Modèle: {view_data.get('model', 'N/A')}")
        print(f"    Type: {view_data.get('arch', {}).get('type', 'N/A')}")

        # Générer les champs
        fields = xml_parser.generate_django_form_fields(view_id)
        print(f"    Champs: {fields}")
        print()


def test_xml_rendering():
    """Test du rendu HTML"""
    print("🎨 Test du rendu HTML...")

    views = xml_parser.get_all_views()

    for view_id, view_data in views.items():
        print(f"  - Test du rendu pour la vue: {view_id}")

        view_type = view_data.get('arch', {}).get('type', 'unknown')

        # Tester avec des données d'exemple selon le type de vue
        if view_type == 'form':
            example_data = {
                'title': 'Note de test',
                'content': 'Contenu de test',
                'category': 'Test Category',
                'note_type': 'NOTE',
                'language': 'fr',
                'difficulty': 'BEGINNER',
                'priority': 'MEDIUM',
                'is_pinned': 'Non',
                'is_archived': 'Non',
            }
        elif view_type == 'tree':
            # Pour une vue liste, utiliser une liste de dictionnaires
            example_data = [
                {
                    'title': 'Note 1',
                    'note_type': 'VOCABULARY',
                    'language': 'fr',
                    'priority': 'HIGH',
                    'created_at': '2025-09-22 15:30',
                    'updated_at': '2025-09-22 15:30',
                },
                {
                    'title': 'Note 2',
                    'note_type': 'GRAMMAR',
                    'language': 'en',
                    'priority': 'MEDIUM',
                    'created_at': '2025-09-22 14:00',
                    'updated_at': '2025-09-22 14:30',
                }
            ]
        else:
            example_data = None

        html = render_xml_view_as_html(view_id, example_data)

        if len(html) > 100:
            print(f"    ✅ HTML généré ({len(html)} caractères)")
        else:
            print(f"    ⚠️  HTML court: {html[:100]}...")
        print()


def test_with_real_data():
    """Test avec des données réelles"""
    print("📊 Test avec des données réelles...")

    # Créer un utilisateur de test si nécessaire
    try:
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            print("    ⚠️  Aucun utilisateur trouvé pour les tests")
            return

        print(f"    👤 Utilisateur de test: {user.username}")

        # Créer une catégorie de test
        category, created = NoteCategory.objects.get_or_create(
            name="Test XML Category",
            user=user,
            defaults={'description': 'Catégorie créée pour tester l\'intégration XML'}
        )

        if created:
            print(f"    📁 Catégorie créée: {category.name}")
        else:
            print(f"    📁 Catégorie existante: {category.name}")

        # Créer quelques notes de test
        notes_data = [
            {
                'title': 'Note XML Test 1',
                'content': 'Contenu de la première note de test XML',
                'note_type': 'VOCABULARY',
                'language': 'fr',
                'difficulty': 'BEGINNER',
                'priority': 'HIGH',
            },
            {
                'title': 'Note XML Test 2',
                'content': 'Contenu de la deuxième note de test XML',
                'note_type': 'GRAMMAR',
                'language': 'en',
                'difficulty': 'INTERMEDIATE',
                'priority': 'MEDIUM',
            }
        ]

        created_notes = []
        for note_data in notes_data:
            note, created = Note.objects.get_or_create(
                title=note_data['title'],
                user=user,
                defaults={**note_data, 'category': category}
            )
            created_notes.append(note)

            if created:
                print(f"    📝 Note créée: {note.title}")
            else:
                print(f"    📝 Note existante: {note.title}")

        # Tester le rendu avec les vraies données
        views = xml_parser.get_all_views()

        for view_id, view_data in views.items():
            view_type = view_data.get('arch', {}).get('type', 'unknown')
            model_name = view_data.get('model', '')

            if model_name == 'notebook.note':
                print(f"    🔧 Test de rendu pour {view_id} (type: {view_type})")

                if view_type == 'tree':
                    # Pour une vue liste, utiliser toutes les notes
                    data = []
                    for note in created_notes:
                        data.append({
                            'title': note.title,
                            'note_type': note.get_note_type_display(),
                            'language': note.language or '-',
                            'created_at': note.created_at.strftime('%Y-%m-%d %H:%M'),
                        })

                elif view_type == 'form':
                    # Pour une vue formulaire, utiliser une note
                    note = created_notes[0]
                    data = {
                        'title': note.title,
                        'content': note.content,
                        'category': note.category.name if note.category else '',
                        'note_type': note.get_note_type_display(),
                        'language': note.language or '',
                        'difficulty': note.get_difficulty_display() if note.difficulty else '',
                        'priority': note.get_priority_display(),
                        'is_pinned': 'Oui' if note.is_pinned else 'Non',
                        'is_archived': 'Oui' if note.is_archived else 'Non',
                    }
                else:
                    data = None

                html = render_xml_view_as_html(view_id, data)
                print(f"      ✅ HTML généré: {len(html)} caractères")

    except Exception as e:
        print(f"    ❌ Erreur: {e}")


def test_xml_file_parsing():
    """Test du parsing du fichier XML"""
    print("📄 Test du parsing du fichier XML...")

    try:
        # Vérifier que le fichier XML existe et est valide
        import xml.etree.ElementTree as ET
        from pathlib import Path

        xml_file = Path('/mnt/c/Users/louis/WebstormProjects/linguify/backend/apps/notebook/templates/templates.xml')

        if xml_file.exists():
            print(f"    ✅ Fichier XML trouvé: {xml_file}")

            # Parser le fichier
            tree = ET.parse(xml_file)
            root = tree.getroot()

            print(f"    📋 Élément racine: {root.tag}")

            records = root.findall('.//record[@model="ir.ui.view"]')
            print(f"    📊 Nombre de records de vue: {len(records)}")

            for record in records:
                view_id = record.get('id')
                print(f"      - Vue ID: {view_id}")

                for field in record.findall('field'):
                    field_name = field.get('name')
                    field_value = field.text or ''
                    if field_name != 'arch':
                        print(f"        {field_name}: {field_value}")
                    else:
                        print(f"        {field_name}: <structure XML>")
        else:
            print(f"    ❌ Fichier XML non trouvé: {xml_file}")

    except Exception as e:
        print(f"    ❌ Erreur lors du parsing: {e}")


def main():
    """Fonction principale de test"""
    print("🚀 Test de l'intégration XML - Application Notebook")
    print("=" * 60)

    # Tests
    test_xml_file_parsing()
    print()

    test_xml_parser()
    print()

    test_xml_rendering()
    print()

    test_with_real_data()
    print()

    print("✅ Tests terminés!")
    print()

    # Afficher les endpoints disponibles
    print("🌐 Endpoints XML disponibles:")
    print("  - GET  /api/v1/notebook/xml/views/")
    print("  - GET  /api/v1/notebook/xml/views/{view_id}/")
    print("  - GET  /api/v1/notebook/xml/views/{view_id}/html/")
    print("  - POST /api/v1/notebook/xml/views/{view_id}/create/")
    print("  - GET  /api/v1/notebook/xml/views/{view_id}/fields/")
    print("  - GET  /api/v1/notebook/xml/reload/")
    print()

    # Afficher les vues disponibles
    views = xml_parser.get_all_views()
    print("📋 Vues XML disponibles:")
    for view_id in views.keys():
        print(f"  - {view_id}")
    print()

    print("💡 Exemples d'utilisation:")
    for view_id in views.keys():
        print(f"  - http://localhost:8000/api/v1/notebook/xml/views/{view_id}/html/")


if __name__ == '__main__':
    main()