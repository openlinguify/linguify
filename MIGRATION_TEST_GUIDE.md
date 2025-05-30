# 🔄 Guide de Test - Migration Auth0 → Supabase

## ✅ Migration Terminée

La migration de Auth0 vers Supabase a été complétée avec succès !

## 🧪 Tests à Effectuer

### 1. Démarrage des Services

#### Backend (Django)
```bash
cd backend
poetry run python manage.py runserver 8000
```

#### Frontend (Next.js)
```bash
cd frontend  
npm run dev
```

### 2. Tests d'Authentification

#### ✅ Test d'Inscription
1. Aller sur `http://localhost:3000/register`
2. Remplir le formulaire avec :
   - Email : `test@example.com`
   - Mot de passe : `motdepasse123`
   - Prénom/Nom : `Test User`
3. Cliquer sur "S'inscrire"
4. ✅ **Attendu** : Redirection vers `/dashboard`

#### ✅ Test de Connexion
1. Aller sur `http://localhost:3000/login`  
2. Utiliser les identifiants créés lors de l'inscription
3. Cliquer sur "Se connecter"
4. ✅ **Attendu** : Redirection vers `/dashboard`

#### ✅ Test OAuth (Optionnel)
1. Sur la page de connexion, cliquer sur "Google" / "GitHub"
2. Autoriser l'application
3. ✅ **Attendu** : Redirection vers `/dashboard`

#### ✅ Test de Déconnexion
1. Une fois connecté, aller aux paramètres utilisateur
2. Cliquer sur "Déconnexion"
3. ✅ **Attendu** : Redirection vers page d'accueil

### 3. Vérifications Backend

#### ✅ API Supabase
```bash
# Test endpoints Supabase
curl -X POST http://localhost:8000/api/auth/supabase/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "motdepasse123"}'
```

#### ✅ Base de Données
1. Vérifier que les utilisateurs apparaissent dans Supabase Dashboard
2. Vérifier que les données sont synchronisées avec Django

### 4. Vérifications Frontend

#### ✅ Console Browser
- Plus d'erreurs "Auth0 configuration incomplete"
- Plus d'erreurs "Auth session missing" 
- Navigation fluide entre les pages

#### ✅ State Management
- State utilisateur persistant après refresh
- Redirections automatiques pour pages protégées

## 🔧 Configuration Actuelle

### Backend
- ✅ Base de données : PostgreSQL Supabase
- ✅ Authentification : `SupabaseAuthentication`
- ✅ Endpoints : `/api/auth/supabase/*`

### Frontend  
- ✅ Provider : `SupabaseAuthProvider`
- ✅ Service : `supabaseAuthService`
- ✅ UI : Formulaires modernes de connexion/inscription

## 🐛 Dépannage

### Erreur "Session Missing"
- Normal lors du premier chargement
- Ne devrait plus apparaître après connexion

### Erreur de Connexion DB
```bash
# Vérifier la connectivité Supabase
cd backend
poetry run python manage.py check
```

### Erreur CORS
- Vérifier `CORS_ALLOWED_ORIGINS` dans settings.py
- Vérifier les URLs dans `.env.local`

## 🔄 Migration des Utilisateurs

Pour migrer les utilisateurs existants d'Auth0 vers Supabase :

1. **Export Auth0** : Exporter les utilisateurs depuis Auth0 Dashboard
2. **Script de Migration** : Créer un script pour importer dans Supabase
3. **Synchronisation** : Mapper les IDs Auth0 → Supabase dans Django

## 🗑️ Nettoyage (Plus tard)

Une fois la migration validée :

1. Supprimer l'ancien `AuthProvider` (Auth0)
2. Nettoyer les variables d'environnement Auth0
3. Supprimer les dépendances `@auth0/auth0-react`
4. Mettre à jour la documentation

## 🎉 Fonctionnalités Disponibles

- ✅ Connexion email/mot de passe
- ✅ Inscription avec métadonnées
- ✅ OAuth (Google, GitHub, Facebook)
- ✅ Réinitialisation de mot de passe  
- ✅ Sessions persistantes
- ✅ Déconnexion sécurisée
- ✅ API authentifiée backend
- ✅ Interface utilisateur moderne

---

**La migration vers Supabase est terminée et prête à être testée ! 🚀**