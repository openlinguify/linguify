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
        # Check if tables already exist before creating them
        migrations.RunSQL(
            sql=[
                # Only create RevisionSettings if it doesn't exist
                """
                CREATE TABLE IF NOT EXISTS revision_revisionsettings (
                    id BIGSERIAL PRIMARY KEY,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    default_study_mode VARCHAR(20) NOT NULL DEFAULT 'spaced',
                    default_difficulty VARCHAR(20) NOT NULL DEFAULT 'normal',
                    cards_per_session INTEGER NOT NULL DEFAULT 20,
                    default_session_duration INTEGER NOT NULL DEFAULT 20,
                    required_reviews_to_learn INTEGER NOT NULL DEFAULT 3,
                    auto_advance BOOLEAN NOT NULL DEFAULT true,
                    spaced_repetition_enabled BOOLEAN NOT NULL DEFAULT true,
                    initial_interval_easy INTEGER NOT NULL DEFAULT 4,
                    initial_interval_normal INTEGER NOT NULL DEFAULT 2,
                    initial_interval_hard INTEGER NOT NULL DEFAULT 1,
                    multiplier_easy DOUBLE PRECISION NOT NULL DEFAULT 2.5,
                    multiplier_normal DOUBLE PRECISION NOT NULL DEFAULT 1.3,
                    multiplier_hard DOUBLE PRECISION NOT NULL DEFAULT 0.8,
                    daily_reminder_enabled BOOLEAN NOT NULL DEFAULT true,
                    reminder_time TIME NOT NULL DEFAULT '19:00:00',
                    notification_frequency VARCHAR(20) NOT NULL DEFAULT 'daily',
                    streak_notifications BOOLEAN NOT NULL DEFAULT true,
                    achievement_notifications BOOLEAN NOT NULL DEFAULT true,
                    enable_animations BOOLEAN NOT NULL DEFAULT true,
                    auto_play_audio BOOLEAN NOT NULL DEFAULT false,
                    keyboard_shortcuts_enabled BOOLEAN NOT NULL DEFAULT true,
                    show_progress_stats BOOLEAN NOT NULL DEFAULT true,
                    theme_preference VARCHAR(10) NOT NULL DEFAULT 'auto',
                    user_id BIGINT NOT NULL UNIQUE REFERENCES authentication_user(id) ON DELETE CASCADE
                );
                """,
                # Only create RevisionSessionConfig if it doesn't exist
                """
                CREATE TABLE IF NOT EXISTS revision_revisionsessionconfig (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    session_duration INTEGER NOT NULL,
                    cards_count INTEGER NOT NULL,
                    study_mode VARCHAR(20) NOT NULL,
                    difficulty_override VARCHAR(20) NOT NULL DEFAULT '',
                    include_new_cards BOOLEAN NOT NULL DEFAULT true,
                    include_review_cards BOOLEAN NOT NULL DEFAULT true,
                    include_failed_cards BOOLEAN NOT NULL DEFAULT true,
                    is_default BOOLEAN NOT NULL DEFAULT false,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    user_id BIGINT NOT NULL REFERENCES authentication_user(id) ON DELETE CASCADE
                );
                """
            ],
            reverse_sql=[
                "DROP TABLE IF EXISTS revision_revisionsettings;",
                "DROP TABLE IF EXISTS revision_revisionsessionconfig;"
            ]
        ),
    ]