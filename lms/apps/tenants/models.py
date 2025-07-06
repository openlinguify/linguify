from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
import uuid

class Organization(models.Model):
    """Main organization model - stored in the master database"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    domain = models.CharField(max_length=255, unique=True, null=True, blank=True)
    
    # Database information
    database_name = models.CharField(max_length=100, unique=True)
    
    # Organization details
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    country = models.CharField(max_length=2, blank=True)
    
    # Subscription info
    plan = models.CharField(max_length=50, default='trial')
    max_students = models.IntegerField(default=100)
    max_instructors = models.IntegerField(default=10)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lms_organizations'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.database_name:
            # Generate database name from slug
            self.database_name = f"lms_org_{self.slug.replace('-', '_')}"
        super().save(*args, **kwargs)


class OrganizationUser(AbstractUser):
    """User model for the master database - links users to organizations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizations = models.ManyToManyField(
        Organization,
        through='OrganizationMembership',
        related_name='users'
    )
    
    class Meta:
        db_table = 'lms_organization_users'


class OrganizationMembership(models.Model):
    """Links users to organizations with roles"""
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    ]
    
    user = models.ForeignKey(OrganizationUser, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_default = models.BooleanField(default=False)
    joined_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'lms_organization_memberships'
        unique_together = ['user', 'organization']
    
    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"