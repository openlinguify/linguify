# Generated migration for ProfanityWord model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_commentlike_commentreport_comment_is_edited_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfanityWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(db_index=True, max_length=100)),
                ('language', models.CharField(choices=[('en', 'English'), ('fr', 'French'), ('es', 'Spanish'), ('nl', 'Dutch')], default='en', max_length=5)),
                ('severity', models.CharField(choices=[('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')], default='mild', max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Profanity Word',
                'verbose_name_plural': 'Profanity Words',
                'indexes': [
                    models.Index(fields=['word', 'language'], name='blog_profanityword_word_lang_idx'),
                    models.Index(fields=['is_active'], name='blog_profanityword_is_active_idx'),
                    models.Index(fields=['severity'], name='blog_profanityword_severity_idx'),
                ],
            },
        ),
        migrations.AlterUniqueTogether(
            name='profanityword',
            unique_together={('word', 'language')},
        ),
    ]