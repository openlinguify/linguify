# Render Dashboard Configuration

Since Render is currently using dashboard settings instead of render.yaml, here are the exact commands to paste into the Render dashboard:

## Build Command:
```bash
export DJANGO_SETTINGS_MODULE=portal.settings && python3 -m pip install --upgrade pip && python3 -m pip install -r requirements.txt && python3 manage.py collectstatic --noinput && python3 manage.py migrate
```

## Start Command:
```bash
export DJANGO_SETTINGS_MODULE=portal.settings && gunicorn portal.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## Alternative: Clear Dashboard Commands

To use render.yaml instead:
1. Go to Render dashboard
2. Clear both "Build Command" and "Start Command" fields (leave them completely empty)
3. Save settings
4. Trigger new deployment

This will force Render to use the render.yaml configuration.

## Environment Variables Required:
- DJANGO_SETTINGS_MODULE=portal.settings
- DJANGO_ENV=production
- DEBUG=False
- SECRET_KEY=(your secret key)
- DATABASE_URL=(your database URL)
- ALLOWED_HOSTS=openlinguify.com,www.openlinguify.com,linguify-portal.onrender.com