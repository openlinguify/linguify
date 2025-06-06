#!/bin/bash

echo "🔍 Diagnostic JWT pour Linguify"
echo "================================"

cd backend

# Activer l'environnement virtuel si il existe
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "⚠️  Pas d'environnement virtuel trouvé"
fi

echo "🐍 Version Python:"
python --version 2>/dev/null || python3 --version

echo ""
echo "📦 Packages JWT installés:"
pip list | grep -i jwt || echo "Aucun package JWT trouvé"

echo ""
echo "🧪 Test du module JWT:"
python -c "
try:
    import jwt
    print('✅ Module jwt importé')
    
    if hasattr(jwt, 'decode'):
        print('✅ jwt.decode disponible')
    else:
        print('❌ jwt.decode manquant')
    
    if hasattr(jwt, 'InvalidTokenError'):
        print('✅ jwt.InvalidTokenError disponible')
    else:
        print('❌ jwt.InvalidTokenError manquant')
    
    if hasattr(jwt, '__version__'):
        print(f'📦 Version: {jwt.__version__}')
    
    # Test basique
    test_payload = {'test': 'data'}
    test_secret = 'test_secret'
    
    token = jwt.encode(test_payload, test_secret, algorithm='HS256')
    decoded = jwt.decode(token, test_secret, algorithms=['HS256'])
    
    if decoded == test_payload:
        print('✅ Test JWT complet réussi')
    else:
        print('❌ Test JWT échoué')
        
except ImportError as e:
    print(f'❌ Module jwt non trouvé: {e}')
except Exception as e:
    print(f'❌ Erreur JWT: {e}')
"

echo ""
echo "🔧 Pour corriger les problèmes JWT:"
echo "pip uninstall jwt pyjwt -y"
echo "pip install PyJWT"
echo ""
echo "Puis redémarrez avec: ./run.sh"