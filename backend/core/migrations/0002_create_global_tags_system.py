# Generated migration for the global tags system

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('authentication', '0001_initial'),  # assuming authentication has initial migration
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('color', models.CharField(default='#3B82F6', max_length=7)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('usage_count_total', models.PositiveIntegerField(default=0)),
                ('usage_count_notebook', models.PositiveIntegerField(default=0)),
                ('usage_count_todo', models.PositiveIntegerField(default=0)),
                ('usage_count_calendar', models.PositiveIntegerField(default=0)),
                ('usage_count_revision', models.PositiveIntegerField(default=0)),
                ('usage_count_documents', models.PositiveIntegerField(default=0)),
                ('usage_count_community', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('is_favorite', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='linguify_tags', to='authentication.user')),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
                'db_table': 'core_tag',
                'ordering': ['name'],
                'indexes': [
                    models.Index(fields=['user', 'name'], name='core_tag_user_name_idx'),
                    models.Index(fields=['user', 'is_active'], name='core_tag_user_active_idx'),
                    models.Index(fields=['user', 'is_favorite'], name='core_tag_user_favorite_idx'),
                    models.Index(fields=['user', 'usage_count_total'], name='core_tag_user_usage_idx'),
                    models.Index(fields=['created_at'], name='core_tag_created_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='TagRelation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('app_name', models.CharField(max_length=50)),
                ('model_name', models.CharField(max_length=50)),
                ('object_id', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tag_relations', to='authentication.user')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations', to='core.tag')),
            ],
            options={
                'verbose_name': 'Tag Relation',
                'verbose_name_plural': 'Tag Relations',
                'db_table': 'core_tagrelation',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['app_name', 'model_name', 'object_id'], name='core_tagrel_content_idx'),
                    models.Index(fields=['tag', 'app_name'], name='core_tagrel_tag_app_idx'),
                    models.Index(fields=['created_by', 'app_name'], name='core_tagrel_user_app_idx'),
                    models.Index(fields=['created_at'], name='core_tagrel_created_idx'),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(fields=('user', 'name'), name='unique_tag_per_user'),
        ),
        migrations.AddConstraint(
            model_name='tagrelation',
            constraint=models.UniqueConstraint(fields=('tag', 'app_name', 'model_name', 'object_id'), name='unique_tag_object_relation'),
        ),
    ]