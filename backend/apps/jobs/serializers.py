from rest_framework import serializers
from .models import Department, JobPosition, JobApplication


class DepartmentSerializer(serializers.ModelSerializer):
    position_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'position_count']
    
    def get_position_count(self, obj):
        return obj.positions.filter(is_active=True).count()


class JobPositionListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    salary_range = serializers.CharField(read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = JobPosition
        fields = [
            'id', 'title', 'department_name', 'location', 
            'employment_type', 'experience_level', 'salary_range',
            'posted_date', 'closing_date', 'is_featured', 'is_open'
        ]


class JobPositionDetailSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    salary_range = serializers.CharField(read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    application_count = serializers.SerializerMethodField()
    
    class Meta:
        model = JobPosition
        fields = [
            'id', 'title', 'department', 'location', 'employment_type', 
            'experience_level', 'description', 'requirements', 
            'responsibilities', 'benefits', 'salary_range', 
            'application_email', 'application_url', 'posted_date', 
            'closing_date', 'is_featured', 'is_open', 'application_count'
        ]
    
    def get_application_count(self, obj):
        return obj.applications.count()


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = [
            'position', 'first_name', 'last_name', 'email', 
            'phone', 'cover_letter', 'resume_file', 'resume_url', 'portfolio_url', 
            'linkedin_url'
        ]
    
    def validate_email(self, value):
        position = self.initial_data.get('position')
        if position and JobApplication.objects.filter(
            position_id=position, email=value
        ).exists():
            raise serializers.ValidationError(
                "You have already applied for this position."
            )
        return value


class JobApplicationSerializer(serializers.ModelSerializer):
    position_title = serializers.CharField(source='position.title', read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'position_title', 'full_name', 'email', 'phone',
            'cover_letter', 'resume_file', 'resume_url', 'portfolio_url', 'linkedin_url',
            'status', 'applied_at'
        ]