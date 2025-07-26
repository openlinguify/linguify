# Generated manually to fix transaction_id field constraint

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0038_add_marketplace_fields'),  # Latest migration
    ]

    operations = [
        migrations.AlterField(
            model_name='studentcourse',
            name='transaction_id',
            field=models.CharField(blank=True, default=None, max_length=100, null=True, unique=True),
        ),
    ]