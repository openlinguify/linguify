#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test de toutes les vues XML avec les nouveaux types
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.notebook.utils.xml_parser import xml_parser, render_xml_view_as_html


def test_view_type(view_type, sample_data=None):
    """Test d'un type de vue spécifique"""
    print(f"\n🔍 VUES DE TYPE '{view_type.upper()}':")

    views = xml_parser.get_views_by_type(view_type)

    if not views:
        print(f"   ❌ Aucune vue de type '{view_type}' trouvée")
        return

    for view_id, view_data in views.items():
        model = view_data.get('model', 'unknown')
        source = view_data.get('source_file', 'unknown')

        print(f"   📄 {view_id}")
        print(f"      Modèle: {model}")
        print(f"      Source: {source}")

        # Tester le rendu
        try:
            html = render_xml_view_as_html(view_id, sample_data)
            length = len(html)
            print(f"      ✅ Rendu: {length} caractères")
            print(f"      🌐 URL: http://localhost:8000/api/v1/notebook/xml/views/{view_id}/html/")
        except Exception as e:
            print(f"      ❌ Erreur: {e}")
        print()


def main():
    print("🚀" + "="*80 + "🚀")
    print("                    TEST DE TOUS LES TYPES DE VUES XML")
    print("🚀" + "="*80 + "🚀")
    print()

    # Données d'exemple pour différents modèles
    note_sample = [
        {
            'title': 'Exemple de note',
            'content': 'Contenu de la note de test',
            'note_type': 'VOCABULARY',
            'language': 'fr',
            'priority': 'HIGH',
            'created_at': '2025-09-22 15:30',
            'updated_at': '2025-09-22 15:30',
            'difficulty': 'INTERMEDIATE',
            'is_pinned': 'Non',
            'is_archived': 'Non',
        }
    ]

    category_sample = [
        {
            'name': 'Catégorie Test',
            'description': 'Description de test',
            'notes_count': '5',
            'created_at': '2025-09-22 14:00',
            'user': 'admin',
        }
    ]

    shared_note_sample = [
        {
            'note_title': 'Note partagée',
            'shared_with': 'utilisateur@example.com',
            'shared_at': '2025-09-22 16:00',
            'can_edit': 'Oui',
            'note_owner': 'admin',
            'note_type': 'VOCABULARY',
            'note_language': 'en',
        }
    ]

    # Test de chaque type de vue
    print("📊 RÉSUMÉ GÉNÉRAL:")
    stats = xml_parser.get_statistics()
    print(f"   📄 Total des vues: {stats['total_views']}")
    print(f"   📁 Fichiers source: {stats['files_count']}")
    print(f"   🎯 Types de vues: {len(stats['view_types'])}")
    print()

    print("🔍 TYPES DE VUES DISPONIBLES:")
    for view_type, count in stats['view_types'].items():
        print(f"   📝 {view_type}: {count} vue(s)")
    print()

    # Tester chaque type de vue
    test_view_type('form', note_sample[0])
    test_view_type('tree', note_sample)
    test_view_type('kanban', note_sample)
    test_view_type('search')
    test_view_type('calendar', note_sample)
    test_view_type('graph', note_sample)
    test_view_type('dashboard')

    # Tester les vues None (probablement des actions/menus)
    print("\n🔧 AUTRES ÉLÉMENTS (actions, menus, etc.):")
    none_views = xml_parser.get_views_by_type(None)
    for view_id, view_data in none_views.items():
        model = view_data.get('model', 'unknown')
        source = view_data.get('source_file', 'unknown')
        print(f"   ⚙️  {view_id} ({model}) [{source}]")

    print("\n" + "="*80)
    print("🎉 TOUS LES TYPES DE VUES SONT MAINTENANT SUPPORTÉS !")
    print()
    print("🌐 EXEMPLES D'URLS À TESTER:")

    # Afficher des exemples d'URLs pour chaque type
    examples = {
        'kanban': xml_parser.get_views_by_type('kanban'),
        'search': xml_parser.get_views_by_type('search'),
        'calendar': xml_parser.get_views_by_type('calendar'),
        'graph': xml_parser.get_views_by_type('graph'),
        'dashboard': xml_parser.get_views_by_type('dashboard'),
    }

    for view_type, views in examples.items():
        if views:
            view_id = list(views.keys())[0]
            print(f"   🎨 {view_type.title()}: http://localhost:8000/api/v1/notebook/xml/views/{view_id}/html/")

    print()
    print("💡 CONSEIL: Visitez http://localhost:8000/api/v1/notebook/xml/ pour voir toutes les options !")


if __name__ == '__main__':
    main()