# Generated by Django 5.1.10 on 2025-06-20 20:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_name', models.CharField(max_length=100)),
                ('author_email', models.EmailField(max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CommentReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reporter_name', models.CharField(max_length=100)),
                ('reporter_email', models.EmailField(max_length=254)),
                ('reason', models.CharField(choices=[('spam', 'Spam or unwanted commercial content'), ('harassment', 'Harassment or bullying'), ('hate_speech', 'Hate speech or discrimination'), ('inappropriate', 'Inappropriate or offensive content'), ('misinformation', 'False or misleading information'), ('copyright', 'Copyright violation'), ('other', 'Other (please specify)')], max_length=20)),
                ('additional_info', models.TextField(blank=True, help_text='Additional details about the report')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_reviewed', models.BooleanField(default=False)),
                ('moderator_notes', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='is_edited',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='comment',
            name='likes_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='comment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['parent'], name='blog_commen_parent__43ce68_idx'),
        ),
        migrations.AddField(
            model_name='commentlike',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='blog.comment'),
        ),
        migrations.AddField(
            model_name='commentreport',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='blog.comment'),
        ),
        migrations.AddIndex(
            model_name='commentlike',
            index=models.Index(fields=['comment'], name='blog_commen_comment_5259c4_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='commentlike',
            unique_together={('comment', 'author_email')},
        ),
        migrations.AddIndex(
            model_name='commentreport',
            index=models.Index(fields=['comment'], name='blog_commen_comment_f11726_idx'),
        ),
        migrations.AddIndex(
            model_name='commentreport',
            index=models.Index(fields=['is_reviewed'], name='blog_commen_is_revi_695b18_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='commentreport',
            unique_together={('comment', 'reporter_email', 'reason')},
        ),
    ]
