# Production Deployment Guide

## Frontend (Vercel)

### Environment Variables Required

Make sure to set these environment variables in your Vercel project settings:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-actual-anon-key

# Backend API
NEXT_PUBLIC_API_URL=https://linguify-h47a.onrender.com

# Optional Debug Flags (set to false in production)
NEXT_PUBLIC_DEBUG_AUTH=false
NEXT_PUBLIC_DEBUG_API=false
```

### Common Issues

1. **"Invalid URL: /" Error**
   - This usually means Supabase environment variables are not set correctly
   - Check that variables don't have quotes around them in Vercel
   - Ensure no trailing spaces in the values

2. **"Failed to fetch" Error**
   - Often caused by CORS issues between Vercel and Render
   - Check backend CORS configuration

## Backend (Render)

### CORS Configuration

Ensure your Django settings include proper CORS configuration:

```python
# settings.py

# For production
ALLOWED_HOSTS = [
    'linguify-h47a.onrender.com',
    'localhost',
    '127.0.0.1',
]

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://linguify.vercel.app",  # Your Vercel frontend URL
    "https://your-custom-domain.com",  # If you have a custom domain
]

# Or for more flexibility (but less secure)
CORS_ALLOW_ALL_ORIGINS = False  # Set to True only for debugging

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

### Environment Variables for Render

```bash
# Database
DATABASE_URL=your-database-url

# Supabase (if backend needs to verify tokens)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key  # Not the anon key!

# Django
SECRET_KEY=your-secret-key
DEBUG=False
```

## Debugging Production Issues

1. **Check Vercel Function Logs**
   ```bash
   vercel logs
   ```

2. **Check Render Logs**
   - Go to your Render dashboard
   - Check the logs section for your service

3. **Test CORS**
   ```javascript
   // Run this in browser console on your Vercel app
   fetch('https://linguify-h47a.onrender.com/api/health/')
     .then(r => r.json())
     .then(console.log)
     .catch(console.error)
   ```

4. **Verify Environment Variables**
   - Visit `/debug-auth` on your frontend to check Supabase configuration
   - Make sure all values are properly set without placeholder values