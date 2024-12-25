import csv
from course.models import VocabularyList, Lesson

# Charger le fichier CSV
with open('vocabulary_list.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        lesson = Lesson.objects.get(id=row['lesson_id'])  # Associer la leçon via l'ID

        # Ajouter ou mettre à jour les entrées
        VocabularyList.objects.update_or_create(
            lesson=lesson,
            word_en=row['word_en'],
            defaults={
                'word_fr': row['word_fr'],
                'word_es': row['word_es'],
                'word_nl': row['word_nl'],
                'definition_en': row['definition_en'],
                'definition_fr': row['definition_fr'],
                'definition_es': row['definition_es'],
                'definition_nl': row['definition_nl'],
                'example_sentence_en': row['example_sentence_en'],
                'example_sentence_fr': row['example_sentence_fr'],
                'example_sentence_es': row['example_sentence_es'],
                'example_sentence_nl': row['example_sentence_nl'],
                'word_type_en': row['word_type_en'],
                'word_type_fr': row['word_type_fr'],
                'word_type_es': row['word_type_es'],
                'word_type_nl': row['word_type_nl']
            }
        )
print("Importation terminée avec succès !")
