import csv
from course.models import VocabularyList

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

