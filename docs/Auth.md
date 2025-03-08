# Guide d'implémentation du système d'authentification unifié

## Étapes d'implémentation

1. **Créer les fichiers principaux**
   - Copier `authService.ts` dans `src/services/`
   - Copier `AuthProvider.tsx` dans `src/services/`
   - Copier `axiosAuthInterceptor.ts` dans `src/services/`

3. **Mise à jour du fichier _app.tsx ou layout.tsx**
   ```tsx
   // Dans votre fichier racine d'application
   import { AuthProvider } from '@/services/AuthProvider';

   function MyApp({ Component, pageProps }) {
     return (
       <AuthProvider>
         <Component {...pageProps} />
       </AuthProvider>
     );
   }
   ```

4. **Vérifier les variables d'environnement**
   Assurez-vous que les variables Auth0 suivantes sont définies dans votre fichier `.env.local` :
   ```
   NEXT_PUBLIC_AUTH0_DOMAIN=your-domain.auth0.com
   NEXT_PUBLIC_AUTH0_CLIENT_ID=your-client-id
   NEXT_PUBLIC_AUTH0_AUDIENCE=your-api-identifier
   NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```

## Points importants à vérifier

### 1. Vérifier les routes protégées
Pour les routes qui nécessitent une authentification, ajoutez ce code au début de votre composant ou dans votre layout :

```tsx
const { isAuthenticated, isLoading } = useAuthContext();
const router = useRouter();

useEffect(() => {
  if (!isLoading && !isAuthenticated) {
    const returnTo = window.location.pathname;
    router.push(`/login?returnTo=${encodeURIComponent(returnTo)}`);
  }
}, [isAuthenticated, isLoading, router]);
```

### 2. Configuration du callback Auth0
Assurez-vous que votre page de callback est correctement configurée pour traiter la redirection après authentification :

```tsx
// pages/callback.tsx
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuthContext } from '@/services/AuthProvider';

export default function Callback() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthContext();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        // Rediriger vers la page de destination ou la page d'accueil
        const returnTo = router.query.state 
          ? JSON.parse(router.query.state as string)?.returnTo 
          : '/';
        router.replace(returnTo || '/');
      } else {
        // Problème d'authentification
        router.replace('/login?error=authentication_failed');
      }
    }
  }, [isAuthenticated, isLoading, router]);

  return <div>Chargement...</div>;
}
```

### 3. Mettre à jour les services API
Remplacez tous vos appels API par l'utilisation de `apiClient` :

```ts
// Avant
const response = await fetch('api/endpoint', {
  headers: { Authorization: `Bearer ${token}` }
});

// Après
import apiClient from '@/services/axiosAuthInterceptor';
const response = await apiClient.get('/api/endpoint');
```

## Dépannage

### Problème : L'authentification ne persiste pas entre les pages

1. **Vérifier le stockage local** : Ouvrez la console du navigateur, allez dans l'onglet Application -> Local Storage et vérifiez que la clé `auth_state` existe et contient un token valide.

2. **Vérifier les cookies** : Dans l'onglet Application -> Cookies, vérifiez que le cookie `access_token` existe.

3. **Désactiver les blocages de cookies tiers** : Certains navigateurs bloquent les cookies tiers. Assurez-vous que les cookies sont autorisés pour votre domaine.

4. **Vérifier les logs** : Activez les logs de débogage en dev et vérifiez les messages `[Auth]` dans la console.

### Problème : Erreurs 401 persistantes

1. **Vérifier l'expiration du token** : Le token pourrait être expiré. Assurez-vous que la configuration Auth0 est correcte avec `useRefreshTokens: true`.

2. **Vérifier la configuration CORS** : Le backend doit autoriser les requêtes depuis le frontend avec les en-têtes d'authentification.

3. **Vérifier l'audience du token** : Assurez-vous que l'audience configurée dans Auth0 correspond à celle attendue par le backend.

### Problème : Erreurs "Invalid State" lors de l'authentification

Cela peut se produire quand le state Auth0 n'est pas correctement géré. Assurez-vous d'utiliser `cacheLocation: "localstorage"` dans la configuration Auth0.

## Tests à effectuer

1. **Test de la connexion** : Connectez-vous et vérifiez que vous êtes redirigé correctement.
2. **Test de navigation** : Naviguez entre plusieurs pages protégées sans être déconnecté.
3. **Test après rechargement** : Rechargez la page et vérifiez que vous restez connecté.
4. **Test de déconnexion** : Déconnectez-vous et vérifiez que vous êtes redirigé vers la page d'accueil.
5. **Test d'expiration** : Attendez que le token expire et vérifiez qu'il est automatiquement renouvelé.