"""
Django management command pour corriger et compiler les traductions
Corrige les problèmes d'encodage Unicode et compile les traductions
"""

import os
import subprocess
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Corrige et compile les traductions Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--languages',
            nargs='+',
            default=['fr', 'en', 'es', 'nl'],
            help='Langues à traiter (par défaut: fr en es nl)'
        )
        parser.add_argument(
            '--skip-makemessages',
            action='store_true',
            help='Ignorer l\'extraction des messages (makemessages)'
        )
        parser.add_argument(
            '--skip-compilemessages',
            action='store_true',
            help='Ignorer la compilation des messages'
        )
        parser.add_argument(
            '--fix-encoding-only',
            action='store_true',
            help='Corriger uniquement l\'encodage des fichiers sans autre traitement'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🌍 Script de correction et compilation des traductions Django')
        )
        self.stdout.write('=' * 60)
        
        try:
            # Get base directory (should be the backend directory)
            base_dir = settings.BASE_DIR
            self.stdout.write(f'📁 Répertoire de travail: {base_dir}')
            
            # Step 1: Fix translation files encoding
            self.fix_translation_files()
            
            if options['fix_encoding_only']:
                self.stdout.write(
                    self.style.SUCCESS('\n✅ Correction d\'encodage terminée.')
                )
                return
            
            # Step 2: Extract translatable strings (if not skipped)
            if not options['skip_makemessages']:
                self.stdout.write('\n1️⃣ Extraction des chaînes traduisibles...')
                languages = ' -l '.join([''] + options['languages'])
                success = self.run_command(
                    f"python manage.py makemessages{languages} --ignore=env --ignore=venv --ignore=staticfiles --ignore=node_modules",
                    "Extraction des messages traduisibles"
                )
                
                if not success:
                    self.stdout.write(
                        self.style.WARNING('⚠️ Continuons avec la compilation des messages existants...')
                    )
            
            # Step 3: Compile translation messages (if not skipped)
            if not options['skip_compilemessages']:
                self.stdout.write('\n2️⃣ Compilation des traductions...')
                success = self.run_command(
                    "python manage.py compilemessages",
                    "Compilation des fichiers .po en .mo"
                )
                
                if success:
                    self.stdout.write(
                        self.style.SUCCESS('\n🎉 Traductions compilées avec succès !')
                    )
                    self.stdout.write('\n📋 Instructions suivantes :')
                    self.stdout.write('  1. Redémarrez le serveur Django :')
                    self.stdout.write('     python manage.py runserver')
                    self.stdout.write('\n  2. Testez les URLs multilingues :')
                    for lang in options['languages']:
                        self.stdout.write(f'     http://127.0.0.1:8000/set-language/{lang}/')
                    self.stdout.write('\n✨ Le site devrait maintenant s\'afficher dans la langue sélectionnée !')
                else:
                    self.stdout.write(
                        self.style.ERROR('\n❌ Erreur lors de la compilation des traductions')
                    )
                    self.stdout.write('\n💡 Solutions possibles :')
                    self.stdout.write('  1. Installer GNU gettext tools :')
                    self.stdout.write('     - Ubuntu/Debian: sudo apt-get install gettext')
                    self.stdout.write('     - MacOS: brew install gettext')
                    self.stdout.write('     - Windows: installer gettext via MSYS2 ou WSL')
                    self.stdout.write('\n  2. Ou utiliser uniquement la correction d\'encodage :')
                    self.stdout.write('     python manage.py fix_translations --fix-encoding-only')
                    raise CommandError('Compilation impossible sans GNU gettext tools')
            
        except Exception as e:
            raise CommandError(f'Erreur lors du traitement des traductions: {str(e)}')

    def run_command(self, command, description):
        """Execute a command and show result"""
        self.stdout.write(f"🔄 {description}...")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                capture_output=True, 
                text=True,
                cwd=settings.BASE_DIR
            )
            self.stdout.write(self.style.SUCCESS(f"✅ {description} - Succès"))
            if result.stdout:
                self.stdout.write(f"   Output: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f"❌ {description} - Erreur"))
            if e.stderr:
                self.stdout.write(f"   Error: {e.stderr.strip()}")
            return False

    def fix_translation_files(self):
        """Fix encoding issues in translation files"""
        locale_dir = os.path.join(settings.BASE_DIR, 'locale')
        
        if not os.path.exists(locale_dir):
            self.stdout.write(
                self.style.WARNING(f'⚠️ Répertoire locale non trouvé: {locale_dir}')
            )
            return
        
        self.stdout.write('🔧 Correction des fichiers de traduction...')
        
        # Remove corrupted .mo files
        mo_count = 0
        for root, dirs, files in os.walk(locale_dir):
            for file in files:
                if file.endswith('.mo'):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        self.stdout.write(f"  🗑️ Supprimé: {file_path}")
                        mo_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f"  ⚠️ Impossible de supprimer {file_path}: {e}")
                        )
        
        if mo_count > 0:
            self.stdout.write(f"  📊 {mo_count} fichiers .mo supprimés")
        
        # Check .po files for encoding issues
        po_count = 0
        fixed_count = 0
        for root, dirs, files in os.walk(locale_dir):
            for file in files:
                if file.endswith('.po'):
                    po_count += 1
                    file_path = os.path.join(root, file)
                    try:
                        # Try to read with UTF-8
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Ensure proper charset declaration
                        if 'charset=UTF-8' not in content:
                            self.stdout.write(f"  🔧 Correction charset: {file_path}")
                            content = content.replace(
                                'charset=CHARSET',
                                'charset=UTF-8'
                            )
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            fixed_count += 1
                        
                        self.stdout.write(f"  ✅ {file_path}")
                        
                    except UnicodeDecodeError as e:
                        self.stdout.write(
                            self.style.ERROR(f"  ❌ Erreur Unicode dans {file_path}: {e}")
                        )
                        # Try to fix by re-encoding
                        try:
                            with open(file_path, 'r', encoding='latin-1') as f:
                                content = f.read()
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            self.stdout.write(
                                self.style.SUCCESS(f"  🔧 Encodage corrigé: {file_path}")
                            )
                            fixed_count += 1
                        except Exception as e2:
                            self.stdout.write(
                                self.style.ERROR(f"  ❌ Impossible de corriger {file_path}: {e2}")
                            )
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"  ❌ Erreur lors du traitement de {file_path}: {e}")
                        )
        
        self.stdout.write(f"  📊 {po_count} fichiers .po traités, {fixed_count} fichiers corrigés")