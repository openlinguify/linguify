# Generated manually for revision settings models

from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('revision', '0010_add_tags_to_flashcard_deck'),
    ]

    operations = [
        migrations.CreateModel(
            name='RevisionSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_study_mode', models.CharField(choices=[('spaced', 'Répétition espacée'), ('intensive', 'Révision intensive'), ('mixed', 'Mode mixte'), ('custom', 'Personnalisé')], default='spaced', help_text="Mode d'étude par défaut pour les nouvelles sessions", max_length=20)),
                ('default_difficulty', models.CharField(choices=[('easy', 'Facile'), ('normal', 'Normal'), ('hard', 'Difficile'), ('expert', 'Expert')], default='normal', help_text='Niveau de difficulté par défaut', max_length=20)),
                ('default_session_duration', models.PositiveIntegerField(default=20, help_text="Durée par défaut d'une session en minutes", validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(120)])),
                ('cards_per_session', models.PositiveIntegerField(default=20, help_text='Nombre de cartes par session par défaut', validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(100)])),
                ('auto_advance', models.BooleanField(default=True, help_text='Passer automatiquement à la carte suivante après validation')),
                ('spaced_repetition_enabled', models.BooleanField(default=True, help_text="Activer l'algorithme de répétition espacée")),
                ('initial_interval_easy', models.PositiveIntegerField(default=4, help_text='Intervalle initial en jours pour les cartes faciles', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(30)])),
                ('initial_interval_normal', models.PositiveIntegerField(default=2, help_text='Intervalle initial en jours pour les cartes normales', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(30)])),
                ('initial_interval_hard', models.PositiveIntegerField(default=1, help_text='Intervalle initial en jours pour les cartes difficiles', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(30)])),
                ('required_reviews_to_learn', models.PositiveIntegerField(default=3, help_text='Nombre de révisions correctes pour marquer une carte comme apprise', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('reset_on_wrong_answer', models.BooleanField(default=False, help_text='Remettre le compteur à zéro si mauvaise réponse')),
                ('show_progress_stats', models.BooleanField(default=True, help_text='Afficher les statistiques de progression')),
                ('daily_reminder_enabled', models.BooleanField(default=True, help_text='Activer les rappels quotidiens')),
                ('reminder_time', models.TimeField(default='18:00', help_text='Heure des rappels quotidiens')),
                ('notification_frequency', models.CharField(choices=[('daily', 'Quotidienne'), ('weekly', 'Hebdomadaire'), ('custom', 'Personnalisée'), ('disabled', 'Désactivée')], default='daily', help_text='Fréquence des notifications', max_length=20)),
                ('enable_animations', models.BooleanField(default=True, help_text="Activer les animations dans l'interface")),
                ('auto_play_audio', models.BooleanField(default=False, help_text='Lecture automatique de l\'audio (si disponible)')),
                ('keyboard_shortcuts_enabled', models.BooleanField(default=True, help_text='Activer les raccourcis clavier')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='revision_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Paramètres de révision',
                'verbose_name_plural': 'Paramètres de révision',
                'app_label': 'revision',
            },
        ),
        migrations.CreateModel(
            name='RevisionSessionConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nom de cette configuration', max_length=100)),
                ('session_type', models.CharField(choices=[('quick', 'Session rapide'), ('standard', 'Session standard'), ('extended', 'Session étendue'), ('custom', 'Session personnalisée')], default='standard', max_length=20)),
                ('duration_minutes', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(120)])),
                ('target_cards', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(200)])),
                ('include_new_cards', models.BooleanField(default=True)),
                ('include_review_cards', models.BooleanField(default=True)),
                ('include_difficult_cards', models.BooleanField(default=True)),
                ('tags_filter', models.JSONField(blank=True, default=list, help_text='Tags à inclure dans cette session')),
                ('difficulty_filter', models.JSONField(blank=True, default=list, help_text='Niveaux de difficulté à inclure')),
                ('is_default', models.BooleanField(default=False, help_text='Configuration par défaut pour cet utilisateur')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revision_session_configs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Configuration de session',
                'verbose_name_plural': 'Configurations de sessions',
                'app_label': 'revision',
            },
        ),
        migrations.AlterUniqueTogether(
            name='revisionsessionconfig',
            unique_together={('user', 'name')},
        ),
    ]