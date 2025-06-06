# Démarrage Rapide Linguify

## ⚡ Méthode Recommandée (Git Bash/Linux)

### Script Principal
```bash
./run.sh
```
Ce script utilise Poetry pour gérer les dépendances et démarre Django + Next.js automatiquement.

### Arrêter les serveurs
```bash
./stop.sh
```

### Forcer le démarrage (si ports occupés)
```bash
./run.sh --force
```

## ✅ Ce qui fonctionne maintenant

- ✅ Installation automatique de Poetry
- ✅ Gestion des dépendances avec Poetry
- ✅ Django démarre sur port 8000
- ✅ Next.js démarre sur port 3000
- ✅ Migrations automatiques
- ✅ Cleanup propre avec Ctrl+C

## 🔧 Si vous avez des erreurs JWT

### Diagnostic JWT
```bash
./debug-jwt.sh
```

### Correction manuelle JWT
```bash
cd backend
source venv/Scripts/activate  # Windows Git Bash
# ou: source venv/bin/activate  # Linux

pip uninstall jwt pyjwt -y
pip install PyJWT
```

## 🛠️ Méthode Manuelle

### Backend Django
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install poetry

REM Corriger JWT en premier
pip uninstall jwt pyjwt -y
pip install PyJWT

poetry install
python manage.py migrate
python manage.py runserver
```

### Frontend Next.js (dans un autre terminal)
```cmd
cd frontend
npm install
npm run dev
```

## 🐧 Linux/WSL

### Installer les prérequis
```bash
sudo apt update
sudo apt install python3-venv python3-pip
```

### Backend Django
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install poetry

# Corriger JWT
pip uninstall jwt pyjwt -y
pip install PyJWT

poetry install
python manage.py migrate
python manage.py runserver
```

## URLs d'accès

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000  
- **Admin Django** : http://localhost:8000/admin
- **API Docs** : http://localhost:8000/api/docs

## Problèmes Courants

### "Python not found"
- Installez Python depuis https://python.org
- Assurez-vous que Python est dans le PATH

### "poetry: command not found"
```bash
pip install poetry
```

### "npm: command not found"
- Installez Node.js depuis https://nodejs.org

### Ports déjà utilisés
```bash
# Tuer les processus sur les ports
netstat -ano | findstr :8000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

## Développement avec les Nouvelles Règles

### Créer un nouveau module
```bash
./linguify-bin scaffold mon_module custom
```

### Valider avant commit
```bash
./scripts/validate-development.sh mon_module
```

### Configuration de l'environnement complet
```bash
./scripts/setup-dev-environment.sh
```