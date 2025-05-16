# Generated manually on 2025-05-15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0016_alter_user_profile_picture'),
        ('course', '0022_alter_matchingexercise_id_alter_vocabularylist_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestRecap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_en', models.CharField(default='English Title', max_length=255)),
                ('title_fr', models.CharField(default='French Title', max_length=255)),
                ('title_es', models.CharField(default='Spanish Title', max_length=255)),
                ('title_nl', models.CharField(default='Dutch Title', max_length=255)),
                ('description_en', models.TextField(blank=True, null=True)),
                ('description_fr', models.TextField(blank=True, null=True)),
                ('description_es', models.TextField(blank=True, null=True)),
                ('description_nl', models.TextField(blank=True, null=True)),
                ('passing_score', models.FloatField(default=0.7, help_text='Minimum score to pass (0.0-1.0)')),
                ('time_limit', models.PositiveIntegerField(default=600, help_text='Time limit in seconds (0 = no limit)')),
                ('is_active', models.BooleanField(default=True)),
                ('lesson', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recap_tests', to='course.lesson')),
            ],
            options={
                'verbose_name': 'Test Recap',
                'verbose_name_plural': 'Test Recaps',
                'ordering': ['lesson', 'id'],
            },
        ),
        migrations.CreateModel(
            name='TestRecapExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exercise_type', models.CharField(max_length=100)),
                ('exercise_id', models.IntegerField()),
                ('order', models.PositiveIntegerField(default=1)),
                ('test_recap', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='course.testrecap')),
            ],
            options={
                'ordering': ['test_recap', 'order'],
            },
        ),
        migrations.CreateModel(
            name='TestRecapAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('is_passed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('answers', models.JSONField(blank=True, default=dict)),
                ('test_recap', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='course.testrecap')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_attempts', to='authentication.user')),
            ],
            options={
                'ordering': ['-completed_at'],
            },
        ),
    ]