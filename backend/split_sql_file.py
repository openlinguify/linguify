#!/usr/bin/env python
"""
Script pour découper un gros fichier SQL en plus petits morceaux
"""

def split_sql_file(input_file, max_lines=100):
    """Découpe un fichier SQL en morceaux plus petits"""
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        print(f"📄 Fichier original: {total_lines} lignes")
        
        # Découper en morceaux
        chunk_number = 1
        current_chunk = []
        chunk_files = []
        
        for i, line in enumerate(lines):
            current_chunk.append(line)
            
            # Si on atteint la limite ou la fin du fichier
            if len(current_chunk) >= max_lines or i == total_lines - 1:
                # Créer le fichier chunk
                chunk_filename = f"chunk_{chunk_number:03d}.sql"
                with open(chunk_filename, 'w', encoding='utf-8') as chunk_file:
                    # Ajouter les commandes de début
                    chunk_file.write("-- Chunk automatique pour Supabase\n")
                    chunk_file.write("SET client_encoding = 'UTF8';\n")
                    chunk_file.write("SET standard_conforming_strings = on;\n\n")
                    
                    # Écrire le contenu
                    chunk_file.writelines(current_chunk)
                    
                    # Ajouter une ligne de fin
                    chunk_file.write(f"\n-- Fin du chunk {chunk_number}\n")
                
                chunk_files.append(chunk_filename)
                print(f"✅ Créé: {chunk_filename} ({len(current_chunk)} lignes)")
                
                # Réinitialiser pour le prochain chunk
                current_chunk = []
                chunk_number += 1
        
        print(f"\n🎉 Découpage terminé!")
        print(f"📁 {len(chunk_files)} fichiers créés")
        print(f"\n📋 Instructions:")
        print(f"1. Importez chaque fichier dans l'ordre dans Supabase SQL Editor:")
        
        for i, chunk_file in enumerate(chunk_files, 1):
            print(f"   {i}. {chunk_file}")
        
        print(f"\n💡 Chaque fichier est assez petit pour l'interface Supabase")
        
        return chunk_files
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return []

if __name__ == "__main__":
    # Chemin vers votre fichier SQL
    sql_file = r"C:\Users\louis\OneDrive\Bureau\db_linguify.sql"
    
    print("🔧 Découpage du fichier SQL...")
    chunks = split_sql_file(sql_file, max_lines=50)  # 50 lignes par chunk