# Generated manually for revision app learning settings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revision', '0006_alter_flashcarddeck_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='flashcarddeck',
            name='required_reviews_to_learn',
            field=models.PositiveIntegerField(default=3, help_text='Nombre de révisions correctes nécessaires pour marquer une carte comme apprise'),
        ),
        migrations.AddField(
            model_name='flashcarddeck',
            name='auto_mark_learned',
            field=models.BooleanField(default=True, help_text='Marquer automatiquement les cartes comme apprises après X révisions'),
        ),
        migrations.AddField(
            model_name='flashcarddeck',
            name='reset_on_wrong_answer',
            field=models.BooleanField(default=False, help_text='Remettre le compteur à zéro si mauvaise réponse'),
        ),
        migrations.AddField(
            model_name='flashcard',
            name='correct_reviews_count',
            field=models.PositiveIntegerField(default=0, help_text='Nombre de révisions correctes consécutives'),
        ),
        migrations.AddField(
            model_name='flashcard',
            name='total_reviews_count',
            field=models.PositiveIntegerField(default=0, help_text='Nombre total de révisions'),
        ),
    ]