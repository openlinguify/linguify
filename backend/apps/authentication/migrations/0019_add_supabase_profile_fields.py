# Generated manually for adding Supabase profile picture fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0018_rename_authenticat_user_id_f7d69f_idx_authenticat_user_id_632a4e_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_picture_url',
            field=models.URLField(blank=True, help_text='URL de la photo de profil stockée dans Supabase', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_picture_filename',
            field=models.CharField(blank=True, help_text='Nom du fichier dans Supabase Storage', max_length=255, null=True),
        ),
    ]