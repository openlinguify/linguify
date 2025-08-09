# Déploiement de la Documentation OpenLinguify

## Configuration Render.com

### Variables d'environnement à configurer sur Render :

```bash
# Django Core
SECRET_KEY=your-production-secret-key-50-chars-minimum
DEBUG=False
DJANGO_ENV=production

# Hosts autorisés (Render génère automatiquement l'URL)
ALLOWED_HOSTS=.onrender.com,openlinguify-docs.onrender.com,www.openlinguify.com,openlinguify.com

# Sécurité HTTPS (activer pour la production)
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Liens externes
MAIN_SITE_URL=https://www.openlinguify.com
GITHUB_REPO_URL=https://github.com/openlinguify/linguify
DISCORD_URL=https://discord.gg/PJ8uTzSS
```

### Commandes de déploiement automatiques :

1. **Build** : `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
2. **Start** : `gunicorn docs_site.wsgi:application`

## Fichiers de configuration inclus :

- ✅ `render.yaml` - Configuration Render
- ✅ `.env.example` - Template des variables d'environnement  
- ✅ `.env` - Configuration de développement
- ✅ `requirements.txt` - Dépendances Python
- ✅ `.gitignore` - Fichiers à ignorer

## Architecture des liens :

```
www.openlinguify.com (Odoo Vitrine)
├── Lien vers Backend Linguify (Render)
└── Lien vers Documentation (Render)
    ├── Header: Retour vers OpenLinguify.com
    ├── Footer: Retour vers OpenLinguify.com
    └── Footer: Lien GitHub
```

## Test local :

```bash
# Démarrer le serveur
make docs

# Ou manuellement
cd docs
python manage.py runserver 8003
```

URL locale : http://127.0.0.1:8003

## Sécurité :

- ✅ SECRET_KEY depuis variables d'environnement
- ✅ DEBUG=False en production
- ✅ HTTPS forcé en production
- ✅ Headers de sécurité configurés
- ✅ Static files servis par WhiteNoise
- ✅ Variables sensibles dans .env (non commitées)