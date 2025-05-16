from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0027_merge_20250515_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testrecap',
            name='correct_answer',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
    ]