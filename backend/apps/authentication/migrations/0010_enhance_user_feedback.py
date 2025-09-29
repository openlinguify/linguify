# Generated manually for enhanced feedback system
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0009_add_marketing_emails_field'),
    ]

    operations = [
        # Step 1: Add new fields with default values or null=True
        migrations.AddField(
            model_name='userfeedback',
            name='title',
            field=models.CharField(default='Imported feedback', help_text='Brief summary of the feedback', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='category',
            field=models.CharField(
                choices=[
                    ('ui_ux', 'UI/UX'),
                    ('performance', 'Performance'),
                    ('functionality', 'Functionality'),
                    ('content', 'Content'),
                    ('mobile', 'Mobile App'),
                    ('desktop', 'Desktop'),
                    ('account', 'Account Management'),
                    ('payment', 'Payment/Billing'),
                    ('language_learning', 'Language Learning'),
                    ('other', 'Other'),
                ],
                default='other',
                help_text='Category for better organization',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='priority',
            field=models.CharField(
                choices=[
                    ('low', 'Low'),
                    ('medium', 'Medium'),
                    ('high', 'High'),
                    ('critical', 'Critical'),
                ],
                default='medium',
                help_text='Priority level',
                max_length=10
            ),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='status',
            field=models.CharField(
                choices=[
                    ('new', 'New'),
                    ('in_progress', 'In Progress'),
                    ('resolved', 'Resolved'),
                    ('closed', 'Closed'),
                    ('duplicate', 'Duplicate'),
                    ('wont_fix', "Won't Fix"),
                ],
                default='new',
                help_text='Current status',
                max_length=15
            ),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='description',
            field=models.TextField(default='', help_text='Detailed description of the feedback'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='steps_to_reproduce',
            field=models.TextField(blank=True, help_text='For bug reports: steps to reproduce the issue', null=True),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='expected_behavior',
            field=models.TextField(blank=True, help_text='What should have happened', null=True),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='actual_behavior',
            field=models.TextField(blank=True, help_text='What actually happened', null=True),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='browser_info',
            field=models.TextField(blank=True, help_text='Browser, OS, and device information', null=True),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='page_url',
            field=models.URLField(blank=True, help_text='URL where the issue occurred', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='screenshot',
            field=models.ImageField(blank=True, help_text='Optional screenshot of the issue', null=True, upload_to='feedback_screenshots/%Y/%m/'),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='admin_notes',
            field=models.TextField(blank=True, help_text='Internal notes for admins (not visible to users)', null=True),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='assigned_to',
            field=models.ForeignKey(blank=True, help_text='Staff member assigned to handle this feedback', limit_choices_to={'is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_feedbacks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='created_at_new',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='resolved_at',
            field=models.DateTimeField(blank=True, help_text='When the feedback was resolved', null=True),
        ),

        # Step 2: Migrate existing data
        migrations.RunSQL(
            """
            UPDATE authentication_userfeedback
            SET
                title = COALESCE(SUBSTRING(feedback_content FROM 1 FOR 50) || '...', 'Legacy Feedback'),
                description = COALESCE(feedback_content, 'No description provided'),
                created_at_new = COALESCE(feedback_date, NOW()),
                status = 'new',
                priority = 'medium',
                category = 'other'
            WHERE title IS NULL OR title = '';
            """,
            reverse_sql=migrations.RunSQL.noop
        ),

        # Step 3: Update feedback_type choices
        migrations.AlterField(
            model_name='userfeedback',
            name='feedback_type',
            field=models.CharField(
                choices=[
                    ('bug_report', 'Bug Report'),
                    ('feature_request', 'Feature Request'),
                    ('improvement', 'Improvement Suggestion'),
                    ('compliment', 'Compliment'),
                    ('complaint', 'Complaint'),
                    ('question', 'Question/Help'),
                    ('other', 'Other'),
                ],
                default='other',
                help_text='Type of feedback',
                max_length=20
            ),
        ),

        # Step 4: Create new models
        migrations.CreateModel(
            name='FeedbackAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(help_text='Additional file attachment (images, logs, etc.)', upload_to='feedback_attachments/%Y/%m/')),
                ('filename', models.CharField(help_text='Original filename', max_length=255)),
                ('file_size', models.PositiveIntegerField(help_text='File size in bytes')),
                ('content_type', models.CharField(help_text='MIME type of the file', max_length=100)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('feedback', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='authentication.userfeedback')),
            ],
            options={
                'verbose_name': 'Feedback Attachment',
                'verbose_name_plural': 'Feedback Attachments',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='FeedbackResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(help_text='Response message to the user')),
                ('is_internal', models.BooleanField(default=False, help_text='Internal note (not visible to user)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(help_text='Staff member who wrote the response', limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('feedback', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='authentication.userfeedback')),
            ],
            options={
                'verbose_name': 'Feedback Response',
                'verbose_name_plural': 'Feedback Responses',
                'ordering': ['-created_at'],
            },
        ),

        # Step 5: Add indexes and constraints
        migrations.AddIndex(
            model_name='userfeedback',
            index=models.Index(fields=['feedback_type', '-created_at_new'], name='auth_feedb_type_created_idx'),
        ),
        migrations.AddIndex(
            model_name='userfeedback',
            index=models.Index(fields=['status', '-created_at_new'], name='auth_feedb_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='userfeedback',
            index=models.Index(fields=['priority', '-created_at_new'], name='auth_feedb_priority_created_idx'),
        ),
        migrations.AddIndex(
            model_name='userfeedback',
            index=models.Index(fields=['category'], name='auth_feedb_category_idx'),
        ),
        migrations.AddIndex(
            model_name='userfeedback',
            index=models.Index(fields=['user', '-created_at_new'], name='auth_feedb_user_created_idx'),
        ),

        # Step 6: Update model meta options
        migrations.AlterModelOptions(
            name='userfeedback',
            options={
                'ordering': ['-created_at_new'],
                'verbose_name': 'User Feedback',
                'verbose_name_plural': 'User Feedbacks'
            },
        ),

        # Step 7: Final cleanup - remove the temporary created_at_new field and replace with created_at
        migrations.RemoveField(
            model_name='userfeedback',
            name='created_at',
        ),
        migrations.RenameField(
            model_name='userfeedback',
            old_name='created_at_new',
            new_name='created_at',
        ),
        migrations.AlterField(
            model_name='userfeedback',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, blank=True, null=True),
        ),
    ]