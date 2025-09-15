#!/usr/bin/env python
"""
Script de test rapide pour l'archivage automatique
Usage: poetry run python test_archiving.py
"""

import os
import django
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.todo.models import TodoSettings, Task, PersonalStageType

User = get_user_model()

def test_archiving():
    """Test l'archivage automatique en modifiant les dates"""
    
    print("🧪 Test de l'archivage automatique")
    print("=" * 50)
    
    # Récupérer l'utilisateur
    user = User.objects.first()
    print(f"👤 Utilisateur: {user.username}")
    
    # Vérifier les paramètres
    try:
        settings = TodoSettings.objects.get(user=user)
        print(f"⚙️  Archivage activé: {settings.auto_archive_completed}")
        print(f"⚙️  Délai archivage: {settings.auto_archive_days} jours")
        print(f"⚙️  Suppression activée: {settings.auto_delete_archived}")
        print(f"⚙️  Délai suppression: {settings.auto_delete_archive_days} jours")
    except TodoSettings.DoesNotExist:
        print("❌ Aucun paramètre TodoSettings trouvé!")
        return
    
    print("\n" + "=" * 50)
    print("🔍 ANALYSE DES TÂCHES")
    print("=" * 50)
    
    # Compter les tâches par stage
    done_stage = PersonalStageType.objects.filter(user=user, name__iexact='Done').first()
    archives_stage = PersonalStageType.objects.filter(user=user, name__iexact='Archives').first()
    
    if not done_stage:
        print("❌ Stage 'Done' non trouvé!")
        return
        
    if not archives_stage:
        print("❌ Stage 'Archives' non trouvé!")
        return
    
    # Tâches terminées dans Done
    done_tasks = Task.objects.filter(
        user=user, 
        state='1_done', 
        personal_stage_type=done_stage,
        active=True
    )
    
    print(f"📋 Tâches dans 'Done': {done_tasks.count()}")
    
    # Tâches dans Archives  
    archived_tasks = Task.objects.filter(
        user=user,
        personal_stage_type=archives_stage,
        active=True
    )
    
    print(f"📦 Tâches dans 'Archives': {archived_tasks.count()}")
    
    # Afficher quelques tâches Done avec leurs dates
    print("\n📅 Tâches récentes dans 'Done':")
    for task in done_tasks.order_by('-completed_at')[:5]:
        completed_date = task.completed_at or task.updated_at
        days_ago = (timezone.now() - completed_date).days if completed_date else "?"
        print(f"  • {task.title[:30]}... - Terminée il y a {days_ago} jours")
    
    print("\n" + "=" * 50)
    print("🚀 TEST RAPIDE")
    print("=" * 50)
    
    print("\n1️⃣ Créer une tâche test et la vieillir artificiellement...")
    
    # Créer une tâche test
    test_task = Task.objects.create(
        user=user,
        title="TEST ARCHIVAGE - À supprimer après test",
        description="Tâche créée automatiquement pour tester l'archivage",
        state='1_done',
        personal_stage_type=done_stage,
        active=True
    )
    
    # La vieillir artificiellement
    old_date = timezone.now() - timedelta(days=settings.auto_archive_days + 1)
    test_task.completed_at = old_date
    test_task.updated_at = old_date
    test_task.save()
    
    print(f"✅ Tâche créée et vieillie à {old_date.strftime('%Y-%m-%d')}")
    
    print("\n2️⃣ Lancer la commande d'archivage...")
    
    # Importer et lancer la commande
    from django.core.management import call_command
    from io import StringIO
    import sys
    
    # Capturer la sortie
    output = StringIO()
    call_command('archive_completed_tasks', '--user-id', user.id, stdout=output)
    
    result = output.getvalue()
    print("📝 Résultat de l'archivage:")
    print(result)
    
    print("\n3️⃣ Vérifier les résultats...")
    
    # Vérifier si la tâche a été archivée
    test_task.refresh_from_db()
    if test_task.personal_stage_type == archives_stage:
        print("✅ Tâche archivée avec succès!")
    else:
        print("❌ Tâche NON archivée")
    
    print("\n4️⃣ Nettoyer...")
    test_task.delete()
    print("🗑️ Tâche test supprimée")
    
    print("\n" + "=" * 50)
    print("📊 RECOMMANDATIONS")
    print("=" * 50)
    
    if not settings.auto_archive_completed:
        print("⚠️  ACTIVEZ l'archivage automatique dans les paramètres!")
    
    if done_tasks.count() == 0:
        print("💡 Créez des tâches et marquez-les 'Done' pour tester")
    
    print("🔧 Pour tester plus rapidement:")
    print("  1. Réglez les délais à 1 jour au lieu de 30")
    print("  2. Créez une tâche et marquez-la 'Done'")
    print("  3. Cliquez 'Déclencher l'archivage maintenant'")

if __name__ == "__main__":
    test_archiving()