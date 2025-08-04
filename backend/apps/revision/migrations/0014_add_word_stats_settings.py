# Generated manually on 2025-08-01

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('revision', '0013_alter_revisionsessionconfig_options_and_more'),
    ]

    operations = [
        # Add word stats fields to RevisionSettings safely
        migrations.RunSQL(
            sql=[
                "ALTER TABLE revision_revisionsettings ADD COLUMN IF NOT EXISTS show_word_stats BOOLEAN DEFAULT true;",
                "ALTER TABLE revision_revisionsettings ADD COLUMN IF NOT EXISTS stats_display_mode VARCHAR(20) DEFAULT 'detailed';",
                "ALTER TABLE revision_revisionsettings ADD COLUMN IF NOT EXISTS hide_learned_words BOOLEAN DEFAULT false;",
                "ALTER TABLE revision_revisionsettings ADD COLUMN IF NOT EXISTS group_by_deck BOOLEAN DEFAULT false;",
            ],
            reverse_sql=[
                "ALTER TABLE revision_revisionsettings DROP COLUMN IF EXISTS show_word_stats;",
                "ALTER TABLE revision_revisionsettings DROP COLUMN IF EXISTS stats_display_mode;",
                "ALTER TABLE revision_revisionsettings DROP COLUMN IF EXISTS hide_learned_words;",
                "ALTER TABLE revision_revisionsettings DROP COLUMN IF EXISTS group_by_deck;",
            ]
        ),
    ]