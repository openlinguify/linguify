# Guide de Déploiement Render - OpenLinguify

## 🎯 Architecture de Déploiement

### Actuellement déployé
- **Backend uniquement** sur `openlinguify.com` (linguify-backend.onrender.com)

### Architecture cible
- **Portal** sur `openlinguify.com` - Landing page et site public
- **Backend** sur `app.openlinguify.com` - Application SaaS et API
- **LMS** sur `lms.openlinguify.com` - Système éducatif (optionnel)

## 🚀 Étapes de Déploiement

### 1. Préparer le Portal pour la Production

Le portal est maintenant configuré avec :
- ✅ Support de Poetry (`pyproject.toml`)
- ✅ Variables d'environnement (`django-environ`)
- ✅ Configuration base de données (`dj-database-url`)
- ✅ Fichiers statiques (`whitenoise`)
- ✅ Configuration de production

### 2. Déployer les Services sur Render

#### Option A : Déploiement complet (Recommandé)
```bash
# Utiliser le fichier render-complete.yaml
# Ce fichier configure :
# - Portal sur openlinguify.com
# - Backend sur app.openlinguify.com
# - LMS sur lms.openlinguify.com
# - Services partagés (Redis, PostgreSQL)
```

#### Option B : Déploiement par étapes
1. **Étape 1** : Déployer le portal
2. **Étape 2** : Reconfigurer le backend
3. **Étape 3** : Configurer les domaines

### 3. Configuration des Variables d'Environnement

#### Pour le Portal (`linguify-portal`)
```env
SECRET_KEY=your-secret-key
DEBUG=False
DJANGO_ENV=production
ALLOWED_HOSTS=openlinguify.com,www.openlinguify.com,linguify-portal.onrender.com
DATABASE_URL=postgresql://... (fourni par Render)
BACKEND_API_URL=https://app.openlinguify.com
```

#### Pour le Backend (`linguify-backend`)
```env
SECRET_KEY=your-backend-secret-key
DEBUG=False
DJANGO_ENV=production
ALLOWED_HOSTS=app.openlinguify.com,backend.openlinguify.com,linguify-backend.onrender.com
DATABASE_URL=postgresql://... (Supabase ou Render)
BACKEND_URL=https://app.openlinguify.com
PORTAL_URL=https://openlinguify.com
CORS_ALLOWED_ORIGINS=https://openlinguify.com,https://www.openlinguify.com
```

### 4. Configuration des Domaines

Dans Render Dashboard :
1. **linguify-portal** :
   - Domaine principal : `openlinguify.com`
   - Alias : `www.openlinguify.com`

2. **linguify-backend** :
   - Domaine principal : `app.openlinguify.com`
   - Alias : `backend.openlinguify.com`

### 5. Configuration DNS

Dans votre gestionnaire de domaine (ex: Cloudflare) :
```
# A Records ou CNAME
openlinguify.com → linguify-portal.onrender.com
www.openlinguify.com → linguify-portal.onrender.com
app.openlinguify.com → linguify-backend.onrender.com
```

## 🔧 Commandes de Déploiement

### Depuis le dashboard Render
1. Allez sur render.com
2. Créez un nouveau service Web
3. Connectez votre repository GitHub
4. Utilisez la configuration :

**Pour le Portal :**
- Build Command : `pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev && python manage.py collectstatic --noinput && python manage.py migrate`
- Start Command : `gunicorn portal.wsgi:application --bind 0.0.0.0:$PORT`
- Root Directory : `portal`

**Pour le Backend :**
- Build Command : `pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev && python manage.py collectstatic --noinput && python manage.py migrate`
- Start Command : `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT`
- Root Directory : `backend`

### Avec Infrastructure as Code
```bash
# Si vous voulez automatiser avec render.yaml
# Copiez render-complete.yaml vers render.yaml
cp render-complete.yaml render.yaml

# Commitez et poussez
git add render.yaml
git commit -m "Configure dual deployment: portal + backend"
git push origin main
```

## 🎯 Résultat Final

Après déploiement :
- **`openlinguify.com`** → Page d'accueil, blog, jobs, docs
- **`app.openlinguify.com`** → Dashboard utilisateur, API, applications
- **`lms.openlinguify.com`** → LMS éducatif (si déployé)

## ⚠️ Notes Importantes

1. **Migrations** : Les deux services partagent potentiellement la même base de données
2. **Sessions** : Les utilisateurs devront se reconnecter lors du changement
3. **CORS** : Le backend doit autoriser les requêtes depuis le portal
4. **SSL** : Render gère automatiquement les certificats SSL

## 🧪 Test Local

Avant déploiement, testez localement :
```bash
# Terminal 1 - Portal
cd portal
poetry run python manage.py runserver 8001

# Terminal 2 - Backend  
cd backend
poetry run python manage.py runserver 8000

# Vérifiez :
# http://localhost:8001 → Portal
# http://localhost:8000 → Backend
```

## 📞 Étapes Suivantes

1. **Décision** : Voulez-vous déployer le portal immédiatement ?
2. **Backup** : Sauvegardez votre configuration actuelle
3. **Migration** : Planifiez la migration des utilisateurs
4. **Tests** : Testez toutes les fonctionnalités après déploiement