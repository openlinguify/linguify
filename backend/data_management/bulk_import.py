import csv
from course.models import Unit  # Remplacez par votre application et modèle

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
        
        # Insérer massivement avec bulk_create pour optimiser
        Unit.objects.bulk_create(units)
        print(f"{len(units)} unités ajoutées avec succès.")

# Spécifiez le chemin de votre fichier CSV
file_path = "C:/Users/louis/OneDrive/Bureau/content/list_unit.csv"

import_units_from_csv(file_path)




