# Generated manually - Add tags to FlashcardDeck

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revision', '0009_add_language_fields_to_flashcard'),
    ]

    operations = [
        migrations.AddField(
            model_name='flashcarddeck',
            name='tags',
            field=models.JSONField(blank=True, default=list, help_text='Liste des tags pour organiser les decks'),
        ),
    ]