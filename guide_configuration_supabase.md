# Configuration Supabase pour Linguify

## 🎯 Pour désactiver la confirmation d'email (développement)

1. **Allez dans votre dashboard Supabase**
2. **Naviguez vers** : Authentication → Settings → User management
3. **Trouvez** : "Enable email confirmations"
4. **Désactivez** cette option
5. **Sauvegardez**

**Résultat :** Les nouveaux utilisateurs seront connectés immédiatement après inscription.

## 🎯 Pour configurer la redirection après confirmation

1. **Allez dans** : Authentication → URL Configuration
2. **Site URL** : `http://localhost:3000`
3. **Redirect URLs** : 
   ```
   http://localhost:3000/auth/callback
   http://localhost:3000/welcome
   http://localhost:3000/
   ```

## 🎯 Pour personnaliser les emails de confirmation

1. **Allez dans** : Authentication → Email Templates
2. **Modifiez** le template "Confirm signup"
3. **Changez l'URL de confirmation** vers votre domaine

## ⚡ Recommandation actuelle

**Pour le développement :** Désactivez la confirmation d'email
**Pour la production :** Réactivez-la pour la sécurité

Votre composant React gère déjà parfaitement les deux cas !