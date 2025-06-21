#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Script pour synchroniser le blog de développement vers production
"""

import os
import sys
import django
import json

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

def sync_blog_to_production():
    """Synchronise les données du blog de dev vers prod"""
    
    print("🔄 SYNCHRONISATION DU BLOG VERS PRODUCTION")
    print("=" * 50)
    
    # Étape 1: Export depuis développement
    print("\n📤 Étape 1: Export depuis développement...")
    os.environ['DJANGO_ENV'] = 'development'
    django.setup()
    
    from core.blog.models import BlogPost, Category, Tag
    from django.core import serializers
    
    # Exporter les données du blog
    blog_data = []
    
    # Categories
    categories = Category.objects.all()
    blog_data.extend(json.loads(serializers.serialize('json', categories)))
    print(f"✅ {categories.count()} catégories exportées")
    
    # Tags  
    tags = Tag.objects.all()
    blog_data.extend(json.loads(serializers.serialize('json', tags)))
    print(f"✅ {tags.count()} tags exportés")
    
    # Articles
    posts = BlogPost.objects.all()
    blog_data.extend(json.loads(serializers.serialize('json', posts)))
    print(f"✅ {posts.count()} articles exportés")
    
    # Relations many-to-many
    for post in posts:
        for tag in post.tags.all():
            blog_data.append({
                'model': 'blog.blogpost_tags',
                'fields': {
                    'blogpost_id': post.id,
                    'tag_id': tag.id
                }
            })
    
    # Sauvegarde temporaire
    export_file = f"blog_export_{django.utils.timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(blog_data, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Données sauvées dans: {export_file}")
    
    # Étape 2: Import vers production
    print("\n📥 Étape 2: Import vers production...")
    
    # Réinitialiser Django pour la production
    from django.apps import apps
    apps.populate()
    
    os.environ['DJANGO_ENV'] = 'production'
    
    # Redémarrer Django
    import importlib
    from django.conf import settings
    importlib.reload(sys.modules['core.settings'])
    
    # Vérifier la connexion production
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Connexion à Supabase établie")
    except Exception as e:
        print(f"❌ Erreur de connexion à Supabase: {e}")
        return False
    
    # Importer les données
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Nettoyer les tables blog en production
        print("🗑️  Nettoyage des tables blog en production...")
        BlogPost.objects.all().delete()
        Category.objects.all().delete() 
        Tag.objects.all().delete()
        print("✅ Tables blog nettoyées")
        
        # Importer les données
        call_command('loaddata', export_file, verbosity=2)
        print("✅ Données importées avec succès")
        
        # Vérification
        print(f"\n📊 Vérification en production:")
        print(f"- Catégories: {Category.objects.count()}")
        print(f"- Tags: {Tag.objects.count()}")
        print(f"- Articles: {BlogPost.objects.count()}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import: {e}")
        return False
    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(export_file):
            os.remove(export_file)
            print(f"🧹 Fichier temporaire supprimé: {export_file}")
    
    print("\n🎉 Synchronisation du blog terminée avec succès!")
    return True

if __name__ == "__main__":
    sync_blog_to_production()