# Generated migration for revision settings models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('revision', '0011_add_revision_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='RevisionSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('default_study_mode', models.CharField(choices=[('spaced', 'Répétition espacée'), ('intensive', 'Révision intensive'), ('mixed', 'Mode mixte'), ('custom', 'Personnalisé')], default='spaced', max_length=20, verbose_name='Mode d\'étude par défaut')),
                ('default_difficulty', models.CharField(choices=[('easy', 'Facile'), ('normal', 'Normal'), ('hard', 'Difficile'), ('expert', 'Expert')], default='normal', max_length=20, verbose_name='Difficulté par défaut')),
                ('cards_per_session', models.PositiveIntegerField(default=20, verbose_name='Cartes par session')),
                ('default_session_duration', models.PositiveIntegerField(default=20, help_text='Durée en minutes', verbose_name='Durée de session par défaut')),
                ('required_reviews_to_learn', models.PositiveIntegerField(default=3, verbose_name='Révisions nécessaires pour apprendre')),
                ('auto_advance', models.BooleanField(default=True, verbose_name='Passage automatique')),
                ('spaced_repetition_enabled', models.BooleanField(default=True, verbose_name='Répétition espacée activée')),
                ('initial_interval_easy', models.PositiveIntegerField(default=4, help_text='En jours', verbose_name='Intervalle initial facile')),
                ('initial_interval_normal', models.PositiveIntegerField(default=2, help_text='En jours', verbose_name='Intervalle initial normal')),
                ('initial_interval_hard', models.PositiveIntegerField(default=1, help_text='En jours', verbose_name='Intervalle initial difficile')),
                ('multiplier_easy', models.FloatField(default=2.5, verbose_name='Multiplicateur facile')),
                ('multiplier_normal', models.FloatField(default=1.3, verbose_name='Multiplicateur normal')),
                ('multiplier_hard', models.FloatField(default=0.8, verbose_name='Multiplicateur difficile')),
                ('daily_reminder_enabled', models.BooleanField(default=True, verbose_name='Rappel quotidien activé')),
                ('reminder_time', models.TimeField(default='19:00', verbose_name='Heure du rappel')),
                ('notification_frequency', models.CharField(choices=[('daily', 'Quotidienne'), ('weekly', 'Hebdomadaire'), ('custom', 'Personnalisée'), ('disabled', 'Désactivée')], default='daily', max_length=20, verbose_name='Fréquence des notifications')),
                ('streak_notifications', models.BooleanField(default=True, verbose_name='Notifications de série')),
                ('achievement_notifications', models.BooleanField(default=True, verbose_name='Notifications de succès')),
                ('enable_animations', models.BooleanField(default=True, verbose_name='Animations activées')),
                ('auto_play_audio', models.BooleanField(default=False, verbose_name='Audio automatique')),
                ('keyboard_shortcuts_enabled', models.BooleanField(default=True, verbose_name='Raccourcis clavier activés')),
                ('show_progress_stats', models.BooleanField(default=True, verbose_name='Afficher les statistiques')),
                ('theme_preference', models.CharField(choices=[('light', 'Clair'), ('dark', 'Sombre'), ('auto', 'Automatique')], default='auto', max_length=10, verbose_name='Préférence de thème')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='revision_settings', to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
            ],
            options={
                'verbose_name': 'Paramètres de révision',
                'verbose_name_plural': 'Paramètres de révision',
            },
        ),
        migrations.CreateModel(
            name='RevisionSessionConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom de la configuration')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('session_duration', models.PositiveIntegerField(verbose_name='Durée de session (minutes)')),
                ('cards_count', models.PositiveIntegerField(verbose_name='Nombre de cartes')),
                ('study_mode', models.CharField(choices=[('spaced', 'Répétition espacée'), ('intensive', 'Révision intensive'), ('mixed', 'Mode mixte'), ('custom', 'Personnalisé')], max_length=20, verbose_name='Mode d\'étude')),
                ('difficulty_override', models.CharField(blank=True, choices=[('easy', 'Facile'), ('normal', 'Normal'), ('hard', 'Difficile'), ('expert', 'Expert')], max_length=20, verbose_name='Difficulté forcée')),
                ('include_new_cards', models.BooleanField(default=True, verbose_name='Inclure nouvelles cartes')),
                ('include_review_cards', models.BooleanField(default=True, verbose_name='Inclure cartes à réviser')),
                ('include_failed_cards', models.BooleanField(default=True, verbose_name='Inclure cartes échouées')),
                ('is_default', models.BooleanField(default=False, verbose_name='Configuration par défaut')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revision_session_configs', to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
            ],
            options={
                'verbose_name': 'Configuration de session',
                'verbose_name_plural': 'Configurations de session',
                'ordering': ['-is_default', '-created_at'],
            },
        ),
    ]