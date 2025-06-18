# Generated migration for jobs app

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='JobPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('location', models.CharField(max_length=200)),
                ('employment_type', models.CharField(choices=[('full_time', 'Full Time'), ('part_time', 'Part Time'), ('contract', 'Contract'), ('internship', 'Internship'), ('remote', 'Remote')], default='full_time', max_length=20)),
                ('experience_level', models.CharField(choices=[('entry', 'Entry Level'), ('mid', 'Mid Level'), ('senior', 'Senior Level'), ('lead', 'Lead'), ('manager', 'Manager')], default='mid', max_length=20)),
                ('description', models.TextField()),
                ('requirements', models.TextField()),
                ('responsibilities', models.TextField()),
                ('benefits', models.TextField(blank=True)),
                ('salary_min', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('salary_max', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('salary_currency', models.CharField(default='EUR', max_length=3)),
                ('application_email', models.EmailField(max_length=254)),
                ('application_url', models.URLField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('posted_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('closing_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='jobs.department')),
            ],
            options={
                'ordering': ['-posted_date', '-is_featured'],
            },
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('cover_letter', models.TextField()),
                ('resume_url', models.URLField(blank=True)),
                ('portfolio_url', models.URLField(blank=True)),
                ('linkedin_url', models.URLField(blank=True)),
                ('status', models.CharField(choices=[('submitted', 'Submitted'), ('reviewed', 'Under Review'), ('interview', 'Interview Stage'), ('offer', 'Offer Extended'), ('hired', 'Hired'), ('rejected', 'Rejected'), ('withdrawn', 'Withdrawn')], default='submitted', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('applied_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='jobs.jobposition')),
            ],
            options={
                'ordering': ['-applied_at'],
            },
        ),
        migrations.AddIndex(
            model_name='jobposition',
            index=models.Index(fields=['is_active', 'posted_date'], name='jobs_jobpos_is_acti_0e6e85_idx'),
        ),
        migrations.AddIndex(
            model_name='jobposition',
            index=models.Index(fields=['department', 'is_active'], name='jobs_jobpos_departm_c44ba0_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='jobapplication',
            unique_together={('position', 'email')},
        ),
    ]