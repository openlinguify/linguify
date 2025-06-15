#!/usr/bin/env python3
"""
Compilation manuelle des traductions Django sans gettext
Permet de compiler les fichiers .po en .mo directement avec Python
"""

import os
import struct
import array
from email.parser import HeaderParser

def make_mo(po_file_path, mo_file_path):
    """
    Compile un fichier .po en .mo manuellement
    Basé sur la spécification du format .mo de GNU gettext
    """
    
    def parse_po_file(po_file):
        """Parse un fichier .po et retourne un dictionnaire de traductions"""
        translations = {}
        current_msgid = ""
        current_msgstr = ""
        in_msgid = False
        in_msgstr = False
        
        with open(po_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Ignorer les commentaires et lignes vides
                if not line or line.startswith('#'):
                    continue
                
                # Début d'un msgid
                if line.startswith('msgid '):
                    if current_msgid and current_msgstr:
                        translations[current_msgid] = current_msgstr
                    current_msgid = line[6:].strip('"')
                    current_msgstr = ""
                    in_msgid = True
                    in_msgstr = False
                
                # Début d'un msgstr
                elif line.startswith('msgstr '):
                    current_msgstr = line[7:].strip('"')
                    in_msgid = False
                    in_msgstr = True
                
                # Continuation d'une chaîne
                elif line.startswith('"') and line.endswith('"'):
                    content = line[1:-1]
                    if in_msgid:
                        current_msgid += content
                    elif in_msgstr:
                        current_msgstr += content
        
        # Ajouter la dernière traduction
        if current_msgid and current_msgstr:
            translations[current_msgid] = current_msgstr
            
        return translations
    
    def write_mo_file(translations, mo_file):
        """Écrit un fichier .mo à partir des traductions"""
        keys = sorted(translations.keys())
        
        # Ajouter l'en-tête avec les métadonnées
        metadata = {
            "": "Content-Type: text/plain; charset=UTF-8\n"
                "Content-Transfer-Encoding: 8bit\n"
                "Language: fr\n"
        }
        
        # Combiner métadonnées et traductions
        all_translations = {**metadata, **translations}
        keys = sorted(all_translations.keys())
        
        # Structure du fichier .mo
        # Magic number (little endian)
        magic = 0x950412de
        version = 0
        
        # Nombre d'entrées
        num_entries = len(keys)
        
        # Offsets des tables
        msgids_offset = 7 * 4  # Après l'en-tête
        msgstrs_offset = msgids_offset + num_entries * 8
        
        # Calculer les offsets des chaînes
        msgid_offsets = []
        msgstr_offsets = []
        
        # Données des chaînes
        msgids_data = b''
        msgstrs_data = b''
        
        for key in keys:
            # Encoder en UTF-8
            key_bytes = key.encode('utf-8')
            msgid_offsets.append((len(msgids_data), len(key_bytes)))
            msgids_data += key_bytes + b'\x00'
            
            msgstr = all_translations[key]
            msgstr_bytes = msgstr.encode('utf-8')
            msgstr_offsets.append((len(msgstrs_data), len(msgstr_bytes)))
            msgstrs_data += msgstr_bytes + b'\x00'
        
        # Calculer l'offset où commencent les données des chaînes
        strings_offset = msgstrs_offset + num_entries * 8
        
        # Ajuster les offsets
        for i in range(len(msgid_offsets)):
            msgid_offsets[i] = (msgid_offsets[i][0] + strings_offset, msgid_offsets[i][1])
            msgstr_offsets[i] = (msgstr_offsets[i][0] + strings_offset + len(msgids_data), msgstr_offsets[i][1])
        
        # Écrire le fichier .mo
        with open(mo_file, 'wb') as f:
            # En-tête
            f.write(struct.pack('<I', magic))       # Magic number
            f.write(struct.pack('<I', version))     # Version
            f.write(struct.pack('<I', num_entries)) # Nombre d'entrées
            f.write(struct.pack('<I', msgids_offset))  # Offset table msgids
            f.write(struct.pack('<I', msgstrs_offset)) # Offset table msgstrs
            f.write(struct.pack('<I', 0))           # Hash table offset (non utilisé)
            f.write(struct.pack('<I', 0))           # Hash table size (non utilisé)
            
            # Table des offsets msgids
            for offset, length in msgid_offsets:
                f.write(struct.pack('<I', length))
                f.write(struct.pack('<I', offset))
            
            # Table des offsets msgstrs
            for offset, length in msgstr_offsets:
                f.write(struct.pack('<I', length))
                f.write(struct.pack('<I', offset))
            
            # Données des chaînes
            f.write(msgids_data)
            f.write(msgstrs_data)
    
    # Parser le fichier .po et créer le .mo
    try:
        translations = parse_po_file(po_file_path)
        # Filtrer les traductions vides
        translations = {k: v for k, v in translations.items() if k and v}
        
        if translations:
            write_mo_file(translations, mo_file_path)
            return True, len(translations)
        else:
            return False, "Aucune traduction trouvée"
    except Exception as e:
        return False, str(e)

def compile_all_translations():
    """Compile toutes les traductions dans le projet"""
    locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
    
    print("🔨 Compilation manuelle des traductions Django")
    print("=" * 50)
    
    success_count = 0
    error_count = 0
    
    for lang_dir in os.listdir(locale_dir):
        lang_path = os.path.join(locale_dir, lang_dir)
        if not os.path.isdir(lang_path):
            continue
            
        lc_messages_path = os.path.join(lang_path, 'LC_MESSAGES')
        if not os.path.exists(lc_messages_path):
            continue
            
        po_file = os.path.join(lc_messages_path, 'django.po')
        mo_file = os.path.join(lc_messages_path, 'django.mo')
        
        if os.path.exists(po_file):
            print(f"🔄 Compilation {lang_dir}...")
            success, result = make_mo(po_file, mo_file)
            
            if success:
                print(f"  ✅ {lang_dir}: {result} traductions compilées")
                success_count += 1
            else:
                print(f"  ❌ {lang_dir}: Erreur - {result}")
                error_count += 1
        else:
            print(f"  ⚠️ {lang_dir}: Fichier .po introuvable")
    
    print(f"\n📊 Résultats:")
    print(f"  ✅ Réussies: {success_count}")
    print(f"  ❌ Erreurs: {error_count}")
    
    if success_count > 0:
        print(f"\n🎉 Compilation terminée !")
        print(f"📋 Instructions suivantes:")
        print(f"  1. Redémarrez le serveur Django")
        print(f"  2. Testez: http://127.0.0.1:8000/set-language/fr/")
        print(f"  3. Le site devrait s'afficher en français !")
        return True
    else:
        print(f"\n❌ Aucune compilation réussie")
        return False

if __name__ == "__main__":
    success = compile_all_translations()
    if success:
        print("\n✨ Traductions prêtes ! Redémarrez Django et testez les langues.")
    else:
        print("\n💡 Vérifiez les fichiers .po dans le dossier locale/")