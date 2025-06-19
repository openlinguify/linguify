# Generated migration for switching resume storage to Supabase
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_jobapplication_resume_file_and_more'),
    ]

    operations = [
        # Add new fields for Supabase storage first
        migrations.AddField(
            model_name='jobapplication',
            name='resume_file_path',
            field=models.CharField(blank=True, max_length=500, null=True, help_text='Path to resume file in Supabase Storage'),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='resume_original_filename',
            field=models.CharField(blank=True, max_length=255, null=True, help_text='Original filename of the uploaded resume'),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='resume_content_type',
            field=models.CharField(blank=True, max_length=100, null=True, help_text='MIME type of the resume file'),
        ),
        # Then remove the old FileField
        migrations.RemoveField(
            model_name='jobapplication',
            name='resume_file',
        ),
    ]