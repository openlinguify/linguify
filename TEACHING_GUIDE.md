# 🎓 Guide Complet - Système d'Enseignement Linguify

## 📋 Vue d'ensemble

Le système d'enseignement Linguify comprend :
- **CMS** : Interface pour que les professeurs gèrent leurs profils, cours et annonces
- **Backend** : Interface pour que les étudiants trouvent et réservent des cours
- **Synchronisation** : Les données CMS sont synchronisées avec le backend

## 🎯 Accès aux Interfaces

### 👨‍🏫 CMS Professeurs (Port 8002)
**URL** : http://127.0.0.1:8002/teachers/

**Comptes disponibles** :
- **admin** / **admin123** (Superuser + Professeur)
- **prof1** / **prof123** (Marie Dupont)
- **prof2** / **prof123** (Jean Martin)
- **teacher** / **teacher123** (John Doe)

### 👨‍🎓 Interface Étudiants (Port 8000)
**URL** : http://127.0.0.1:8000/teaching/

**Compte étudiant** :
- Utilisez votre compte utilisateur habituel du backend Linguify

### 🔧 Admin Django
**URL** : http://127.0.0.1:8002/admin/
- **Username** : admin
- **Password** : admin123

## 🎨 Fonctionnalités Disponibles

### 📱 CMS Professeurs

#### Dashboard Principal
- ✅ **Statistiques** : Cours total, terminés, gains, évaluations
- ✅ **Prochains cours** : Liste des 5 prochains cours
- ✅ **Actions rapides** : Liens vers les principales fonctions
- ✅ **Statut du profil** : État d'approbation et informations

#### Gestion des Cours (`/teachers/lessons/`)
- ✅ **Liste complète** des cours avec pagination
- ✅ **Filtres** : Par statut, date de début/fin
- ✅ **Actions** : Confirmer, annuler, ajouter des notes
- ✅ **Statuts détaillés** : Programmé, confirmé, en cours, terminé, annulé

#### Planning (`/teachers/availability/`)
- ✅ **Vue hebdomadaire** des disponibilités
- ✅ **Ajout de créneaux** : Par jour de la semaine
- ✅ **Gestion des horaires** : Modification, suppression
- ✅ **Interface intuitive** : Planning visuel clair

#### Annonces (`/teachers/announcements/`)
- ✅ **Création d'annonces** multilingues (FR/EN)
- ✅ **Types** : Promotion, Nouveau cours, Changement d'horaires, Général, Vacances
- ✅ **Promotions** : Pourcentage de remise ou prix spécial
- ✅ **Ciblage** : Par langues et niveaux
- ✅ **Statistiques** : Vues, clics, réservations générées
- ✅ **Mise en avant** : Annonces prioritaires
- ✅ **Aperçu temps réel** lors de la création

### 👨‍🎓 Interface Étudiants

#### Dashboard Teaching (`/teaching/`)
- ✅ **Professeurs disponibles** avec notes et tarifs
- ✅ **Prochains cours** de l'étudiant
- ✅ **Statistiques générales** du système
- ✅ **Accès rapide** à la réservation

#### API Disponibles
- ✅ **`/teaching/api/teachers/`** : Liste des professeurs
- ✅ **`/teaching/api/teachers/{id}/`** : Détail d'un professeur  
- ✅ **`/teaching/api/teachers/{id}/availability/`** : Disponibilités
- ✅ **`/teaching/api/book/`** : Réserver un cours
- ✅ **`/teaching/api/lessons/`** : Cours de l'étudiant

## 📊 Données de Test Disponibles

### Professeurs Créés

1. **Admin Teacher** (cms_id: 1)
   - Langues : Français (natif), English (fluent), Español (intermédiaire)
   - Tarif : €50/h
   - Disponibilités : Lun-Sam avec créneaux variés
   - ⭐ **Annonce active** : "Cours de français - Promotion de rentrée" (-30%)

2. **Marie Dupont** (cms_id: 2)
   - Langues : Français (natif), English (fluent)
   - Tarif : €35/h
   - Spécialité : Conversation et grammaire française

3. **Jean Martin** (cms_id: 3)
   - Langues : English (natif), Español (fluent), Français (intermédiaire)
   - Tarif : €40/h
   - Spécialité : Anglais et espagnol, méthodes modernes

4. **John Doe** (cms_id: 4)
   - Langues : English (natif), Français (intermédiaire)
   - Tarif : €30/h
   - Spécialité : Approche communicative anglais

### Annonce de Test

**🎉 Cours de français - Promotion de rentrée !**
- **Type** : Promotion
- **Remise** : 30%
- **Durée** : 30 jours
- **Langues ciblées** : Français, Anglais
- **Niveaux** : A1, A2, B1, B2
- **Statut** : Active et mise en avant

## 🔄 Comment Tester le Système

### 1. Connexion CMS Professeur
1. Allez sur http://127.0.0.1:8002/teachers/
2. Connectez-vous avec **admin** / **admin123**
3. Explorez le dashboard et les différentes sections

### 2. Création d'une Nouvelle Annonce
1. Dans le CMS, allez sur http://127.0.0.1:8002/teachers/announcements/
2. Cliquez "Nouvelle annonce"
3. Remplissez le formulaire et voyez l'aperçu en temps réel
4. Publiez l'annonce

### 3. Gestion des Disponibilités
1. Allez sur http://127.0.0.1:8002/teachers/availability/
2. Ajoutez de nouveaux créneaux horaires
3. Visualisez votre planning hebdomadaire

### 4. Interface Étudiant
1. Connectez-vous au backend avec votre compte habituel
2. Allez sur http://127.0.0.1:8000/teaching/
3. Voyez la liste des professeurs avec leurs informations
4. *Note* : La réservation nécessite une authentification complète

## 🛠️ Synchronisation des Données

Les données sont actuellement synchronisées manuellement :
- Les professeurs CMS ont été créés dans le backend
- Les disponibilités sont dupliquées
- Les langues enseignées sont synchronisées

**Pour synchroniser de nouvelles données** :
- Utilisez le shell Django backend pour créer des Teacher correspondants
- Respectez les `cms_teacher_id` pour la correspondance

## 🚀 URLs Importantes

### CMS (Port 8002)
- **Dashboard** : http://127.0.0.1:8002/teachers/
- **Cours** : http://127.0.0.1:8002/teachers/lessons/
- **Planning** : http://127.0.0.1:8002/teachers/availability/
- **Annonces** : http://127.0.0.1:8002/teachers/announcements/
- **Admin** : http://127.0.0.1:8002/admin/

### Backend (Port 8000)
- **Teaching** : http://127.0.0.1:8000/teaching/
- **API** : http://127.0.0.1:8000/teaching/api/teachers/

## 💡 Conseils d'Utilisation

1. **Testez les différents rôles** : Connectez-vous avec différents professeurs
2. **Créez du contenu** : Ajoutez des annonces, modifiez les disponibilités
3. **Explorez l'API** : Testez les endpoints avec un client REST
4. **Interface responsive** : Testez sur mobile/tablette
5. **Données réalistes** : Les professeurs ont des profils complets et variés

## 🔧 Développement

Pour ajouter des fonctionnalités :
- **CMS** : Modifiez `/cms/apps/teachers/`
- **Backend** : Modifiez `/backend/apps/teaching/`
- **Synchronisation** : Implémentez dans `/backend/apps/cms_sync/`

Le système est modulaire et extensible ! 🎉