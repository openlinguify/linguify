# Documentation pour l'importation massive de données dans Django

## Objectif

Ce document fournit des instructions détaillées pour effectuer des importations massives de données dans Django en utilisant la méthode :

```python
from data_management.bulk_import import import_units_from_csv
```

Il couvre les étapes pour importer des unités (units), des leçons (lessons) et des listes de vocabulaire (vocabulary lists).

---

## 1. Structure des fichiers CSV

Avant d'importer, assurez-vous que vos fichiers CSV respectent la structure des colonnes définies dans vos modèles Django.

### Comment générer un fichier CSV correctement formaté
1. Ouvrez un tableur comme **Excel** ou **Google Sheets**.
2. Entrez les données dans des colonnes en respectant les en-têtes spécifiés.
3. Allez dans **Fichier → Enregistrer sous** ou **Télécharger**.
4. Sélectionnez le format **CSV UTF-8 (délimité par des virgules)**.
5. Vérifiez que le fichier est bien enregistré avec l'extension **.csv** et encodé en **UTF-8**.

### Exemple : **Units**

```csv
title_en,title_fr,title_es,title_nl,description_en,description_fr,description_es,description_nl,order,level
Greeting,Salutation,Saludo,Begroeting,Learn how to greet,Apprenez à saluer,Aprende a saludar,Leer hoe je begroet,1,A1
Introduction,Présentation,Presentación,Voorstelling,Learn to introduce,Apprenez à vous présenter,Aprende a presentarte,Leer hoe je jezelf voorstelt,2,A1
```

### Exemple : **Vocabulary Lists**

```csv
word_en,word_fr,word_es,word_nl,definition_en,definition_fr,definition_es,definition_nl
apple,pomme,manzana,appel,A fruit,Un fruit,Una fruta,Een vrucht
book,livre,libro,boek,A reading object,Un objet de lecture,Un objeto de lectura,Een leesobject
```

---

## 2. Préparer les scripts d'importation

### Exemple : Script pour importer des unités (**bulk_import.py**)

```python
import csv
from course.models import Unit

def import_units_from_csv(file_path):
    with open(file_path, encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        units = []

        for row in reader:
            unit = Unit(
                title_en=row['title_en'],
                title_fr=row['title_fr'],
                title_es=row['title_es'],
                title_nl=row['title_nl'],
                description_en=row['description_en'],
                description_fr=row['description_fr'],
                description_es=row['description_es'],
                description_nl=row['description_nl'],
                order=int(row['order']),
                level=row['level']
            )
            units.append(unit)

        Unit.objects.bulk_create(units)
        print(f"{len(units)} unités ajoutées avec succès.")
```

### Exemple : Script pour importer des listes de vocabulaire

```python
import csv
from course.models import VocabularyList

def import_vocabularies_from_csv(file_path):
    with open(file_path, encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        vocabularies = []

        for row in reader:
            vocabulary = VocabularyList(
                word_en=row['word_en'],
                word_fr=row['word_fr'],
                word_es=row['word_es'],
                word_nl=row['word_nl'],
                definition_en=row['definition_en'],
                definition_fr=row['definition_fr'],
                definition_es=row['definition_es'],
                definition_nl=row['definition_nl']
            )
            vocabularies.append(vocabulary)

        VocabularyList.objects.bulk_create(vocabularies)
        print(f"{len(vocabularies)} listes de vocabulaire ajoutées avec succès.")
```

---

## 3. Exécuter le script d'importation

### 1. Ouvrir le shell Django :

```bash
python manage.py shell
```

### 2. Importer et exécuter le script pour les unités :

```python
from data_management.bulk_import import import_units_from_csv
import_units_from_csv("C:/Users/louis/OneDrive/Bureau/content/list_unit.csv")
```

### 3. Importer et exécuter le script pour les vocabulaires :

```python
from data_management.bulk_import import import_vocabularies_from_csv
import_vocabularies_from_csv("C:/Users/louis/OneDrive/Bureau/content/vocab_list.csv")
```

---

## 4. Résolution des erreurs fréquentes

### 1. **Erreur : Clé primaire dupliquée**

- Problème : L'ID existe déjà dans la base de données.
- Solution :
  - Supprimez la colonne **id** du fichier CSV pour utiliser l'auto-incrémentation.
  - Ou utilisez `ON CONFLICT` dans le SQL pour ignorer les doublons.

### 2. **Erreur d'encodage UTF-8**

- Problème : Encodage incorrect dans le fichier CSV.
- Solution : Convertir le fichier :

```bash
iconv -f ISO-8859-1 -t UTF-8 input.csv -o output.csv
```

### 3. **Erreur UnicodeEscape**

- Problème : Chemin avec des barres obliques inversées.
- Solution :
  - Utiliser des barres obliques (`/`) ou un chemin brut (`r"path"`).

### 4. **Champ manquant ou mal formaté**

- Vérifiez les colonnes et types de données dans votre modèle et le CSV.

---

## 5. Vérifications post-importation

Après chaque importation, vérifiez les données :

```python
from course.models import Unit
print(Unit.objects.all())

from course.models import VocabularyList
print(VocabularyList.objects.all())
```

---

## 6. Étapes pour de futurs imports

1. Préparer vos fichiers CSV avec des colonnes correctes.
2. Vérifier l'encodage en UTF-8.
3. Lancer le script d'import dans le shell Django.
4. Vérifier les données importées dans l'interface d'administration.

---

## 7. Notes supplémentaires

- Utilisez `bulk_update` pour mettre à jour les données existantes.
- Utilisez `TRUNCATE TABLE` pour nettoyer la table avant un nouvel import si nécessaire.
- Pour des fichiers volumineux, ajoutez un **batch_size** dans `bulk_create` :

```python
Unit.objects.bulk_create(units, batch_size=1000)
```

---
