# Enhanced feedback system - Clean migration
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0009_add_marketing_emails_field'),
    ]

    operations = [
        # Step 1: Add new fields with appropriate defaults or null=True
        migrations.AddField(
            model_name='userfeedback',
            name='title',
            field=models.CharField(max_length=200, help_text='Brief summary of the feedback', default='Feedback'),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='category',
            field=models.CharField(
                max_length=20,
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
                help_text='Category for better organization'
            ),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='priority',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('low', 'Low'),
                    ('medium', 'Medium'),
                    ('high', 'High'),
                    ('critical', 'Critical'),
                ],
                default='medium',
                help_text='Priority level'
            ),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='status',
            field=models.CharField(
                max_length=15,
                choices=[
                    ('new', 'New'),
                    ('in_progress', 'In Progress'),
                    ('resolved', 'Resolved'),
                    ('closed', 'Closed'),
                    ('duplicate', 'Duplicate'),
                    ('wont_fix', "Won't Fix"),
                ],
                default='new',
                help_text='Current status'
            ),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='description',
            field=models.TextField(help_text='Detailed description of the feedback', default='No description provided'),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='steps_to_reproduce',
            field=models.TextField(blank=True, null=True, help_text='For bug reports: steps to reproduce the issue'),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='expected_behavior',
            field=models.TextField(blank=True, null=True, help_text='What should have happened'),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='actual_behavior',
            field=models.TextField(blank=True, null=True, help_text='What actually happened'),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='browser_info',
            field=models.TextField(blank=True, null=True, help_text='Browser, OS, and device information'),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='page_url',
            field=models.URLField(blank=True, null=True, max_length=500, help_text='URL where the issue occurred'),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='screenshot',
            field=models.ImageField(blank=True, null=True, upload_to='feedback_screenshots/%Y/%m/', help_text='Optional screenshot of the issue'),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='admin_notes',
            field=models.TextField(blank=True, null=True, help_text='Internal notes for admins (not visible to users)'),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='assigned_to',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_feedbacks',
                to=settings.AUTH_USER_MODEL,
                limit_choices_to={'is_staff': True},
                help_text='Staff member assigned to handle this feedback'
            ),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='userfeedback',
            name='resolved_at',
            field=models.DateTimeField(blank=True, null=True, help_text='When the feedback was resolved'),
        ),

        # Step 2: Migrate existing data from legacy fields
        migrations.RunSQL(
            """
            UPDATE authentication_userfeedback SET
                title = COALESCE(
                    CASE
                        WHEN LENGTH(feedback_content) > 50 THEN SUBSTRING(feedback_content FROM 1 FOR 50) || '...'
                        WHEN feedback_content IS NOT NULL AND feedback_content != '' THEN feedback_content
                        ELSE 'Legacy Feedback'
                    END,
                    'Legacy Feedback'
                ),
                description = COALESCE(feedback_content, 'No description provided'),
                created_at = COALESCE(feedback_date, NOW())
            WHERE title = 'Feedback' OR description = 'No description provided' OR created_at IS NULL;
            """,
            reverse_sql=migrations.RunSQL.noop
        ),

        # Step 3: Update feedback_type choices
        migrations.AlterField(
            model_name='userfeedback',
            name='feedback_type',
            field=models.CharField(
                max_length=20,
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
                help_text='Type of feedback'
            ),
        ),

        # Step 4: Make legacy fields optional
        migrations.AlterField(
            model_name='userfeedback',
            name='feedback_date',
            field=models.DateTimeField(blank=True, null=True, help_text='Legacy field - use created_at instead'),
        ),
        migrations.AlterField(
            model_name='userfeedback',
            name='feedback_content',
            field=models.TextField(blank=True, null=True, help_text='Legacy field - use description instead'),
        ),

        # Step 5: Create new models
        migrations.CreateModel(
            name='FeedbackAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='feedback_attachments/%Y/%m/', help_text='Additional file attachment (images, logs, etc.)')),
                ('filename', models.CharField(max_length=255, help_text='Original filename')),
                ('file_size', models.PositiveIntegerField(help_text='File size in bytes')),
                ('content_type', models.CharField(max_length=100, help_text='MIME type of the file')),
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
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, limit_choices_to={'is_staff': True}, help_text='Staff member who wrote the response')),
                ('feedback', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='authentication.userfeedback')),
            ],
            options={
                'verbose_name': 'Feedback Response',
                'verbose_name_plural': 'Feedback Responses',
                'ordering': ['-created_at'],
            },
        ),

        # Step 6: Add indexes
        migrations.AddIndex(
            model_name='userfeedback',
            index=models.Index(fields=['feedback_type', '-created_at'], name='auth_feedb_type_created_idx'),
        ),
        migrations.AddIndex(
            model_name='userfeedback',
            index=models.Index(fields=['status', '-created_at'], name='auth_feedb_status_created_idx'),
        ),
        migrations.AddIndex(
            model_name='userfeedback',
            index=models.Index(fields=['priority', '-created_at'], name='auth_feedb_priority_created_idx'),
        ),
        migrations.AddIndex(
            model_name='userfeedback',
            index=models.Index(fields=['category'], name='auth_feedb_category_idx'),
        ),
        migrations.AddIndex(
            model_name='userfeedback',
            index=models.Index(fields=['user', '-created_at'], name='auth_feedb_user_created_idx'),
        ),

        # Step 7: Update model meta options
        migrations.AlterModelOptions(
            name='userfeedback',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'User Feedback',
                'verbose_name_plural': 'User Feedbacks'
            },
        ),
    ]