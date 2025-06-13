# Guide pour tester la production en local

## Méthodes disponibles

### 1. Build et Start simple
```bash
npm run build
npm run start
```
Accédez à http://localhost:3000

### 2. Avec variables d'environnement de production
```bash
npm run prod:local
```

### 3. Test complet de production (recommandé)
```bash
npm run test:prod
```

### 4. Simuler le domaine de production

#### Sur Windows (en tant qu'administrateur) :
Ajoutez cette ligne à `C:\Windows\System32\drivers\etc\hosts` :
```
127.0.0.1 www.openlinguify.com
127.0.0.1 openlinguify.com
```

#### Sur Linux/Mac :
Ajoutez cette ligne à `/etc/hosts` :
```
127.0.0.1 www.openlinguify.com
127.0.0.1 openlinguify.com
```

Puis accédez à http://www.openlinguify.com:3000

### 5. Vérifier le comportement du middleware

Pour déboguer le middleware en production locale, vous pouvez temporairement ajouter des logs :

```typescript
// Dans middleware.ts
const isProduction = host.includes('openlinguify.com') || process.env.NODE_ENV === 'production';
console.log('Production check:', { host, isProduction, NODE_ENV: process.env.NODE_ENV });
```

## Variables d'environnement importantes

Créez un fichier `.env.production.local` :
```env
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://www.openlinguify.com
```

## Différences avec Vercel

- **Vercel** : Variables d'environnement automatiques, CDN, edge functions
- **Local** : Pas de CDN, pas d'edge functions, mais même comportement applicatif

## Commandes utiles

- `npm run build` : Compile l'application
- `npm run start` : Lance le serveur de production
- `npm run analyze` : Analyse la taille du bundle
- `npm run type-check` : Vérifie les types TypeScript