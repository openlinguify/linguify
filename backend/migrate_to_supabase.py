#!/usr/bin/env python
"""
Script de migration des données vers Supabase
"""
import os
import sys
import django
import psycopg2
from django.conf import settings

# Ajouter le répertoire racine au Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def create_migration_script():
    """Créer un script SQL de migration"""
    
    # Configuration des bases
    local_config = {
        'host': 'localhost',
        'database': 'db_linguify_dev',
        'user': 'postgres',
        'password': 'azerty',
        'port': 5432
    }
    
    supabase_config = {
        'host': 'aws-0-eu-west-3.pooler.supabase.com',
        'database': 'postgres',
        'user': 'postgres.epafiiysxzqcjlgupnft',
        'password': 'fGfoZsPSfI02GA5o',
        'port': 6543
    }
    
    print("🔧 Generating migration script...")
    
    # Tables à migrer dans l'ordre (pour respecter les clés étrangères)
    tables_order = [
        'auth_group',
        'auth_permission',
        'auth_group_permissions',
        'django_content_type',
        'authentication_user',
        'authentication_user_groups',
        'authentication_user_user_permissions',
        'course_unit',
        'course_lesson',
        'course_contentlesson',
        'course_vocabularylist',
        'course_matchingexercise',
        'course_theorycontent',
        'course_numbers',
        'course_fillblankexercise',
        'course_speakingexercise',
        'course_testrecap',
        'course_testrecapquestion',
        'course_testrecapresult',
        'revision_flashcarddeck',
        'revision_flashcard',
        'notebook_note',
        'notification_notification',
        'jobs_jobposition',
        'language_ai_aiconversation',
    ]
    
    migration_script = "-- Migration script for Linguify to Supabase\n"
    migration_script += "-- Generated automatically\n\n"
    
    try:
        # Connexion à la base locale
        local_conn = psycopg2.connect(**local_config)
        local_cursor = local_conn.cursor()
        
        print("✅ Connected to local database")
        
        for table in tables_order:
            try:
                # Vérifier si la table existe
                local_cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    );
                """)
                
                table_exists = local_cursor.fetchone()[0]
                
                if table_exists:
                    # Compter les lignes
                    local_cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    count = local_cursor.fetchone()[0]
                    
                    if count > 0:
                        print(f"📋 Exporting {table}: {count} rows")
                        
                        # Générer DELETE pour nettoyer
                        migration_script += f"-- Table: {table}\n"
                        migration_script += f"DELETE FROM {table};\n"
                        
                        # Générer les données
                        local_cursor.execute(f"SELECT * FROM {table};")
                        rows = local_cursor.fetchall()
                        
                        if rows:
                            # Obtenir les noms des colonnes
                            local_cursor.execute(f"""
                                SELECT column_name 
                                FROM information_schema.columns 
                                WHERE table_name = '{table}' 
                                ORDER BY ordinal_position;
                            """)
                            columns = [row[0] for row in local_cursor.fetchall()]
                            
                            # Générer les INSERT
                            for row in rows:
                                values = []
                                for value in row:
                                    if value is None:
                                        values.append('NULL')
                                    elif isinstance(value, str):
                                        # Échapper les apostrophes
                                        escaped = value.replace("'", "''")
                                        values.append(f"'{escaped}'")
                                    elif isinstance(value, bool):
                                        values.append('TRUE' if value else 'FALSE')
                                    else:
                                        values.append(str(value))
                                
                                migration_script += f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
                        
                        migration_script += f"\n"
                    else:
                        print(f"⚠️  Table {table} is empty")
                else:
                    print(f"⚠️  Table {table} does not exist")
                    
            except Exception as e:
                print(f"❌ Error with table {table}: {e}")
                continue
        
        # Sauvegarder le script
        script_path = "migration_to_supabase.sql"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(migration_script)
        
        print(f"\n✅ Migration script generated: {script_path}")
        print(f"📁 File size: {os.path.getsize(script_path) / 1024 / 1024:.2f} MB")
        
        local_conn.close()
        
        return script_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    script_path = create_migration_script()
    if script_path:
        print(f"\n🚀 Next steps:")
        print(f"1. Review the generated file: {script_path}")
        print(f"2. Execute it on Supabase using psql:")
        print(f"   psql 'postgresql://postgres.epafiiysxzqcjlgupnft:fGfoZsPSfI02GA5o@aws-0-eu-west-3.pooler.supabase.com:6543/postgres' -f {script_path}")