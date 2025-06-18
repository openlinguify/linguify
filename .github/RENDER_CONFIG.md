# Configuration Render

## Services IDs à configurer dans GitHub Secrets

Ajoutez ces secrets dans GitHub → Settings → Secrets and variables → Actions :

```
RENDER_STAGING_SERVICE_ID=srv-xxxxxxxxxx  # À récupérer depuis Render Dashboard
RENDER_PRODUCTION_SERVICE_ID=srv-yyyyyy   # À récupérer depuis Render Dashboard
```

## API Keys déjà configurées dans le workflow

- **Staging**: `rnd_sTW1YJFvnzWxHWfGWdMBKtmwiZfi`
- **Production**: `rnd_LYvNUTDvyHgmiPbryBLPTUl7qyHI`

## Comment trouver les Service IDs

1. Aller sur [Render Dashboard](https://dashboard.render.com)
2. Cliquer sur votre service
3. L'ID est dans l'URL : `https://dashboard.render.com/web/srv-XXXXXXXXX`
4. Copier la partie `srv-XXXXXXXXX`

## Flux de déploiement

```
develop → tests → auto-merge → staging → tests → deploy staging → auto-merge → main → deploy production
```

## Variables d'environnement Render

Assurez-vous d'avoir configuré ces variables dans chaque service Render :

### Staging & Production
- `SECRET_KEY`
- `DEBUG=False`
- `DJANGO_ENV=production`
- `ALLOWED_HOSTS`
- `BACKEND_URL`
- `SUPABASE_*` variables
- `EMAIL_*` variables
- `REDIS_URL`