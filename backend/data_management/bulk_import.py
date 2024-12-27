import os
import csv
from course.models import Unit, VocabularyList


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


def import_vocabulary_lists_from_csv(file_path):
    with open(file_path, encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        vocabulary_lists = []

        for row in reader:
            vocabulary_list = VocabularyList(

                lesson_id=int(row['lesson_id']),
                word_en=row['word_en'],
                word_fr=row['word_fr'],
                word_es=row['word_es'],
                word_nl=row['word_nl'],
                definition_en=row['definition_en'],
                definition_fr=row['definition_fr'],
                definition_es=row['definition_es'],
                definition_nl=row['definition_nl'],
                example_sentence_en=row['example_sentence_en'],
                example_sentence_fr=row['example_sentence_fr'],
                example_sentence_es=row['example_sentence_es'],
                example_sentence_nl=row['example_sentence_nl'],
                word_type_en=row['word_type_en'],
                word_type_fr=row['word_type_fr'],
                word_type_es=row['word_type_es'],
                word_type_nl=row['word_type_nl']
            )
            vocabulary_lists.append(vocabulary_list)
        
        
        VocabularyList.objects.bulk_create(vocabulary_lists)
        print(f"{len(vocabulary_lists)} listes de vocabulaire ajoutées avec succès.")


file_path = "C:/Users/louis/OneDrive/Bureau/content/vocabulary_list.csv"
import_vocabulary_lists_from_csv(file_path)

