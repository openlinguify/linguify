#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test du nouveau système XML multi-fichiers
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.notebook.utils.xml_parser import xml_parser, reload_xml_parser


def main():
    print("🚀" + "="*70 + "🚀")
    print("          TEST DU SYSTÈME XML MULTI-FICHIERS")
    print("🚀" + "="*70 + "🚀")
    print()

    # Recharger le parser pour s'assurer qu'on a les dernières données
    parser = reload_xml_parser()

    # Obtenir les statistiques
    stats = parser.get_statistics()

    print("📊 STATISTIQUES GÉNÉRALES:")
    print(f"   📄 Fichiers XML parsés: {stats['files_count']}")
    print(f"   👁️  Vues totales: {stats['total_views']}")
    print(f"   ⚡ Actions: {stats['total_actions']}")
    print(f"   📋 Menus: {stats['total_menus']}")
    print()

    print("🔍 RÉPARTITION PAR TYPE DE VUE:")
    for view_type, count in stats['view_types'].items():
        print(f"   📝 {view_type}: {count} vue(s)")
    print()

    print("📁 FICHIERS SOURCE:")
    for file in stats['source_files']:
        print(f"   📄 {file}")
    print()

    print("🎯 VUES PAR MODÈLE:")
    models = {}
    for view_id, view_data in parser.get_all_views().items():
        model = view_data.get('model', 'unknown')
        if model not in models:
            models[model] = []
        models[model].append(view_id)

    for model, views in models.items():
        print(f"   🏗️  {model}: {len(views)} vue(s)")
        for view_id in views[:3]:  # Afficher max 3 exemples
            view_data = parser.get_view(view_id)
            view_type = view_data.get('arch', {}).get('type', 'unknown')
            source = view_data.get('source_file', 'unknown')
            print(f"      - {view_id} ({view_type}) [{source}]")
        if len(views) > 3:
            print(f"      ... et {len(views) - 3} autres")
        print()

    print("⚡ ACTIONS DISPONIBLES:")
    for action_id, action_data in parser.get_all_actions().items():
        name = action_data.get('name', 'Sans nom')
        model = action_data.get('res_model', 'unknown')
        source = action_data.get('source_file', 'unknown')
        print(f"   🎯 {action_id}: {name} ({model}) [{source}]")
    print()

    print("📋 STRUCTURE DES MENUS:")
    menus = parser.get_all_menus()

    # Organiser les menus par hiérarchie
    root_menus = {k: v for k, v in menus.items() if not v.get('parent')}

    for menu_id, menu_data in root_menus.items():
        name = menu_data.get('name', 'Sans nom')
        source = menu_data.get('source_file', 'unknown')
        print(f"   📁 {name} ({menu_id}) [{source}]")

        # Chercher les sous-menus
        sub_menus = {k: v for k, v in menus.items() if v.get('parent') == menu_id}
        for sub_id, sub_data in sub_menus.items():
            sub_name = sub_data.get('name', 'Sans nom')
            sub_source = sub_data.get('source_file', 'unknown')
            action = sub_data.get('action', '')
            print(f"      └── 📝 {sub_name} ({sub_id}) [{sub_source}]")
            if action:
                print(f"           ⚡ Action: {action}")
    print()

    print("🔥 EXEMPLES D'UTILISATION:")
    print("   🌐 Toutes les vues kanban:")
    kanban_views = parser.get_views_by_type('kanban')
    for view_id in list(kanban_views.keys())[:3]:
        print(f"      http://localhost:8000/api/v1/notebook/xml/views/{view_id}/html/")

    print()
    print("   📊 Vues pour le modèle notebook.note:")
    note_views = parser.get_views_by_model('notebook.note')
    for view_id in list(note_views.keys())[:3]:
        view_type = note_views[view_id].get('arch', {}).get('type', 'unknown')
        print(f"      {view_id} ({view_type}): /api/v1/notebook/xml/views/{view_id}/html/")

    print()
    print("🎉 TEST TERMINÉ AVEC SUCCÈS !")
    print(f"   Votre système XML supporte maintenant {stats['total_views']} vues réparties sur {stats['files_count']} fichiers !")


if __name__ == '__main__':
    main()