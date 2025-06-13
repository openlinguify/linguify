# Système de Redirection d'Authentification

## Vue d'ensemble

Le système de redirection d'authentification de Linguify gère intelligemment où rediriger les utilisateurs non authentifiés selon l'environnement :

- **Développement** : Redirige vers `/login` pour l'expérience développeur
- **Production** : Redirige vers `/home` (landing page) pour l'expérience utilisateur

## Architecture

### 1. Utilitaire Central (`/src/core/utils/environment.ts`)

Centralise toute la logique de détection d'environnement :

```typescript
// Détection d'environnement
isProductionEnvironment(host?: string): boolean

// Destination de redirection
getUnauthenticatedRedirect(host?: string): '/home' | '/login'

// Information complète d'environnement
getEnvironmentInfo(host?: string): EnvironmentInfo
```

### 2. Middleware (`/frontend/middleware.ts`)

- **Niveau** : Edge Runtime (serveur)
- **Responsabilité** : Première ligne de défense pour les routes protégées
- **Logique** : Utilise `getUnauthenticatedRedirect()` pour déterminer la destination

```typescript
// Routes protégées
if (PROTECTED_PATHS.some(path => pathname === path || pathname.startsWith(path))) {
  if (!isAuthenticated) {
    const redirectDestination = getUnauthenticatedRedirect(host);
    return NextResponse.redirect(new URL(redirectDestination, request.url));
  }
}
```

### 3. Layout Dashboard (`/src/app/(dashboard)/layout.tsx`)

- **Niveau** : Client React
- **Responsabilité** : Deuxième ligne de défense pour les pages dashboard
- **Logique** : Utilise `getUnauthenticatedRedirect()` pour la cohérence

```typescript
const redirectDestination = getUnauthenticatedRedirect();

if (redirectDestination === '/home') {
  window.location.href = '/home';
} else {
  login(pathname); // Redirige vers /login avec returnTo
}
```

## Critères de Détection de Production

### Côté Serveur (Middleware)
1. Hostname contient `openlinguify.com`
2. Hostname contient `linguify.vercel.app`
3. Variable `VERCEL_ENV=production`

### Côté Client (Layout)
1. Hostname contient `openlinguify.com`
2. Hostname contient `linguify.vercel.app`
3. Variable `NODE_ENV=production`

### Override pour Tests
Variable `NEXT_PUBLIC_FORCE_PRODUCTION_BEHAVIOR=true` force le comportement production.

## Configuration par Environnement

### Développement (`.env.local`)
```env
# Pas de configuration spéciale nécessaire
# Comportement par défaut : redirection vers /login
```

### Production Locale (`.env.production.local`)
```env
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://www.openlinguify.com

# Pour forcer le comportement production en test :
# NEXT_PUBLIC_FORCE_PRODUCTION_BEHAVIOR=true
```

### Production Vercel
```env
# Variables automatiques :
VERCEL_ENV=production
# Hostname : www.openlinguify.com ou linguify.vercel.app
```

## Flux de Redirection

### Utilisateur Non Authentifié

#### En Développement :
```
localhost:3000 → middleware → /login?returnTo=/
```

#### En Production :
```
www.openlinguify.com → middleware → /home
```

### Routes Protégées

#### En Développement :
```
localhost:3000/learning → middleware → /login?returnTo=/learning
```

#### En Production :
```
www.openlinguify.com/learning → middleware → /home
```

## Tests

### Test Production en Local
```bash
# 1. Build avec configuration production
npm run build

# 2. Start avec environnement production
npm run start

# 3. Tester sur localhost:3000
# Devrait rediriger vers /home si NODE_ENV=production
```

### Test avec Domaine Simulé
```bash
# 1. Modifier /etc/hosts (Linux/Mac) ou C:\Windows\System32\drivers\etc\hosts (Windows)
127.0.0.1 www.openlinguify.com

# 2. Accéder à http://www.openlinguify.com:3000
# Devrait rediriger vers /home automatiquement
```

## Débogage

### Logs Disponibles
- `[Middleware] Environment Info` : Information d'environnement côté serveur
- `[Dashboard Layout] Environment Info` : Information d'environnement côté client
- `[Auth Flow] Redirecting to X` : Logs de redirection

### Variables de Debug
Activez les logs détaillés en définissant dans le middleware :
```typescript
const DEBUG_MODE = true; // Ligne 8 de middleware.ts
```

## Maintenance

### Ajouter un Nouveau Critère de Production
1. Modifier `isProductionEnvironment()` dans `/src/core/utils/environment.ts`
2. Tester en local avec `npm run build && npm run start`
3. Déployer et vérifier en production

### Ajouter une Nouvelle Route Protégée
1. Ajouter à `PROTECTED_PATHS` dans `/frontend/middleware.ts`
2. Le système de redirection s'appliquera automatiquement

## Sécurité

- ✅ Le middleware s'exécute côté serveur (plus sécurisé)
- ✅ Le layout agit comme fallback côté client
- ✅ Pas d'exposition de logique sensible côté client
- ✅ Variables d'environnement appropriées pour chaque contexte

## Troubleshooting

### Problème : Toujours redirigé vers /login en production
- Vérifiez que `NODE_ENV=production`
- Vérifiez le hostname dans les logs
- Utilisez `NEXT_PUBLIC_FORCE_PRODUCTION_BEHAVIOR=true` temporairement

### Problème : Pas de redirection en développement
- Vérifiez que la route est dans `PROTECTED_PATHS`
- Vérifiez les logs du middleware
- Vérifiez l'état d'authentification