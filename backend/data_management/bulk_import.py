import os
import csv
from course.models import Unit


def validate_file_path(file_path: str) -> None:
    """Vérifie si le fichier existe et est accessible"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier '{file_path}' n'existe pas.")
    if not os.path.isfile(file_path):
        raise ValueError(f"'{file_path}' n'est pas un fichier.")
    if not file_path.endswith('.csv'):
        raise ValueError(f"'{file_path}' n'est pas un fichier CSV.")

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

file_path = "C:/Users/louis/OneDrive/Bureau/content/list_unit.csv"

import_units_from_csv(file_path)
