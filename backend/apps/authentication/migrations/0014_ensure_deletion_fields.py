from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0013_user_deletion_date_user_deletion_scheduled_at_and_more'),
    ]

    operations = [
        # Ensure all deletion fields exist and have the correct properties
        migrations.AlterField(
            model_name='user',
            name='is_pending_deletion',
            field=models.BooleanField(default=False, help_text='Whether the account is scheduled for deletion'),
        ),
        migrations.AlterField(
            model_name='user',
            name='deletion_scheduled_at',
            field=models.DateTimeField(blank=True, help_text='When the account deletion was requested', null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='deletion_date',
            field=models.DateTimeField(blank=True, help_text='When the account will be permanently deleted', null=True),
        ),
    ]