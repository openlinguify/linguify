# Generated migration to allow spontaneous applications
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_migrate_to_supabase_storage'),
    ]

    operations = [
        # Remove the unique constraint
        migrations.AlterUniqueTogether(
            name='jobapplication',
            unique_together=set(),
        ),
        # Allow position to be null for spontaneous applications
        migrations.AlterField(
            model_name='jobapplication',
            name='position',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='jobs.jobposition'),
        ),
    ]