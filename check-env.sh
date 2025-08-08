#!/bin/bash

# Script pour vérifier l'environnement de tous les projets Linguify

echo "🔍 Vérification des environnements Linguify..."
echo ""

echo "📦 PORTAL (port 8080):"
cd portal 2>/dev/null
if [ -f "venv/bin/python" ]; then
    python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
import django
django.setup()
from django.conf import settings
print('  Mode:', 'Développement' if settings.DEBUG else 'Production')
print('  Hosts:', settings.ALLOWED_HOSTS[:3] if len(settings.ALLOWED_HOSTS) > 3 else settings.ALLOWED_HOSTS)
" 2>/dev/null || echo "  ❌ Erreur de configuration"
else
    echo "  ❌ Environnement virtuel non trouvé"
fi
cd ..
echo ""

echo "🎓 LMS (port 8001):"
cd lms 2>/dev/null
if [ -f "venv/bin/python" ]; then
    python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()
from django.conf import settings
print('  Mode:', 'Développement' if settings.DEBUG else 'Production')
print('  Hosts:', settings.ALLOWED_HOSTS[:3] if len(settings.ALLOWED_HOSTS) > 3 else settings.ALLOWED_HOSTS)
" 2>/dev/null || echo "  ❌ Erreur de configuration"
else
    echo "  ❌ Environnement virtuel non trouvé"
fi
cd ..
echo ""

echo "⚙️ BACKEND (port 8000):"
cd backend 2>/dev/null
if command -v poetry >/dev/null 2>&1; then
    poetry run python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from django.conf import settings
print('  Mode:', 'Développement' if settings.DEBUG else 'Production')
print('  Hosts:', settings.ALLOWED_HOSTS[:3] if len(settings.ALLOWED_HOSTS) > 3 else settings.ALLOWED_HOSTS)
" 2>/dev/null || echo "  ❌ Erreur de configuration"
else
    echo "  ❌ Poetry non trouvé"
fi
cd ..
echo ""

echo "👨‍🏫 CMS (port 8002):"
cd cms 2>/dev/null  
if [ -f "venv/bin/python" ]; then
    python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings')
import django
django.setup()
from django.conf import settings
print('  Mode:', 'Développement' if settings.DEBUG else 'Production')
print('  Hosts:', settings.ALLOWED_HOSTS[:3] if len(settings.ALLOWED_HOSTS) > 3 else settings.ALLOWED_HOSTS)
" 2>/dev/null || echo "  ❌ Erreur de configuration"
else
    echo "  ❌ Environnement virtuel non trouvé"
fi
cd ..
echo ""

echo "💡 Astuce: Utilisez './check-env.sh' ou ajoutez 'alias check-env=./check-env.sh' à votre .bashrc"