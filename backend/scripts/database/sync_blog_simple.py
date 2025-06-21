#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

"""
Script simple pour synchroniser le blog de développement vers production
"""

import os
import sys
import django

# Configuration Django pour développement
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ['DJANGO_ENV'] = 'development'
django.setup()

def main():
    print("🔄 SYNCHRONISATION SIMPLE DU BLOG")
    print("=" * 40)
    
    # Import des modèles
    from core.blog.models import BlogPost, Category, Tag
    
    # Étape 1: Collecter les données de dev
    print("\n📤 Collecte des données de développement...")
    
    dev_categories = list(Category.objects.all().values())
    dev_tags = list(Tag.objects.all().values()) 
    dev_posts = list(BlogPost.objects.all().values())
    
    # Relations many-to-many
    dev_post_tags = []
    for post in BlogPost.objects.all():
        for tag in post.tags.all():
            dev_post_tags.append({
                'post_id': post.id,
                'tag_id': tag.id
            })
    
    print(f"✅ {len(dev_categories)} catégories")
    print(f"✅ {len(dev_tags)} tags") 
    print(f"✅ {len(dev_posts)} articles")
    print(f"✅ {len(dev_post_tags)} relations post-tag")
    
    # Étape 2: Basculer vers production et insérer
    print("\n📥 Basculement vers production...")
    
    # Changer d'environnement
    os.environ['DJANGO_ENV'] = 'production'
    
    # Reconfigurer Django
    from django.conf import settings
    settings.configure()
    django.setup()
    
    from core.blog.models import BlogPost, Category, Tag
    from django.db import transaction
    
    print("✅ Connecté à Supabase")
    
    # Transaction pour tout faire en une fois
    with transaction.atomic():
        print("\n🗑️  Nettoyage des tables...")
        BlogPost.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        
        print("📝 Création des catégories...")
        category_mapping = {}
        for cat_data in dev_categories:
            old_id = cat_data.pop('id')
            new_cat = Category.objects.create(**cat_data)
            category_mapping[old_id] = new_cat.id
            
        print("🏷️  Création des tags...")
        tag_mapping = {}
        for tag_data in dev_tags:
            old_id = tag_data.pop('id')
            new_tag = Tag.objects.create(**tag_data)
            tag_mapping[old_id] = new_tag.id
            
        print("📄 Création des articles...")
        post_mapping = {}
        for post_data in dev_posts:
            old_id = post_data.pop('id')
            old_category_id = post_data.pop('category_id', None)
            
            if old_category_id:
                post_data['category_id'] = category_mapping[old_category_id]
                
            new_post = BlogPost.objects.create(**post_data)
            post_mapping[old_id] = new_post
            
        print("🔗 Création des relations post-tag...")
        for relation in dev_post_tags:
            post = post_mapping[relation['post_id']]
            tag_id = tag_mapping[relation['tag_id']]
            tag = Tag.objects.get(id=tag_id)
            post.tags.add(tag)
    
    print("\n📊 Vérification finale:")
    print(f"- Catégories: {Category.objects.count()}")
    print(f"- Tags: {Tag.objects.count()}")
    print(f"- Articles: {BlogPost.objects.count()}")
    
    print("\n🎉 Synchronisation terminée avec succès!")

if __name__ == "__main__":
    main()