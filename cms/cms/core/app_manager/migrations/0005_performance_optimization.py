# Generated performance optimization migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_manager', '0004_add_app_order_field'),  # Correct migration dependency
    ]

    operations = [
        # Add database indexes for performance (without CONCURRENTLY in migrations)
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_app_enabled_code ON app_manager_app (is_enabled, code) WHERE is_enabled = TRUE;",
            reverse_sql="DROP INDEX IF EXISTS idx_app_enabled_code;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_app_enabled_order ON app_manager_app (is_enabled, \"order\", display_name) WHERE is_enabled = TRUE;",
            reverse_sql="DROP INDEX IF EXISTS idx_app_enabled_order;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_userapp_settings_user ON app_manager_userappsettings (user_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_userapp_settings_user;"
        ),
    ]