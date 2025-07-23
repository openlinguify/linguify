"""
Serializers for CMS sync endpoints.
"""
from rest_framework import serializers

class CMSTeacherSerializer(serializers.Serializer):
    """Serializer for teacher data from CMS."""
    cms_teacher_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    full_name = serializers.CharField(max_length=200)
    bio_en = serializers.CharField(required=False, allow_blank=True)
    bio_fr = serializers.CharField(required=False, allow_blank=True)
    bio_es = serializers.CharField(required=False, allow_blank=True)
    bio_nl = serializers.CharField(required=False, allow_blank=True)
    hourly_rate = serializers.DecimalField(max_digits=6, decimal_places=2)
    years_experience = serializers.IntegerField(required=False, default=0)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, required=False, default=0)
    total_hours_taught = serializers.IntegerField(required=False, default=0)

class CMSUnitSerializer(serializers.Serializer):
    """Serializer for unit data from CMS."""
    teacher_cms_id = serializers.IntegerField()
    title_en = serializers.CharField(max_length=100)
    title_fr = serializers.CharField(max_length=100)
    title_es = serializers.CharField(max_length=100)
    title_nl = serializers.CharField(max_length=100)
    description_en = serializers.CharField(required=False, allow_blank=True)
    description_fr = serializers.CharField(required=False, allow_blank=True)
    description_es = serializers.CharField(required=False, allow_blank=True)
    description_nl = serializers.CharField(required=False, allow_blank=True)
    level = serializers.ChoiceField(choices=[
        ('A1', 'A1'), ('A2', 'A2'), ('B1', 'B1'), 
        ('B2', 'B2'), ('C1', 'C1'), ('C2', 'C2')
    ])
    order = serializers.IntegerField(default=1)

class CMSChapterSerializer(serializers.Serializer):
    """Serializer for chapter data from CMS."""
    unit_id = serializers.IntegerField()
    title_en = serializers.CharField(max_length=100)
    title_fr = serializers.CharField(max_length=100)
    title_es = serializers.CharField(max_length=100)
    title_nl = serializers.CharField(max_length=100)
    description_en = serializers.CharField(required=False, allow_blank=True)
    description_fr = serializers.CharField(required=False, allow_blank=True)
    description_es = serializers.CharField(required=False, allow_blank=True)
    description_nl = serializers.CharField(required=False, allow_blank=True)
    theme = serializers.CharField(max_length=50)
    order = serializers.IntegerField(default=1)
    style = serializers.ChoiceField(choices=[
        ('Open Linguify', 'Open Linguify Style'),
        ('OpenLinguify', 'OpenLinguify Style'),
        ('custom', 'Custom Style')
    ], default='Open Linguify')
    points_reward = serializers.IntegerField(default=100)

class CMSLessonSerializer(serializers.Serializer):
    """Serializer for lesson data from CMS."""
    unit_id = serializers.IntegerField()
    chapter_id = serializers.IntegerField(required=False, allow_null=True)
    title_en = serializers.CharField(max_length=100)
    title_fr = serializers.CharField(max_length=100)
    title_es = serializers.CharField(max_length=100)
    title_nl = serializers.CharField(max_length=100)
    description_en = serializers.CharField(required=False, allow_blank=True)
    description_fr = serializers.CharField(required=False, allow_blank=True)
    description_es = serializers.CharField(required=False, allow_blank=True)
    description_nl = serializers.CharField(required=False, allow_blank=True)
    lesson_type = serializers.ChoiceField(choices=[
        ('vocabulary', 'Vocabulary'),
        ('grammar', 'Grammar'),
        ('culture', 'Culture'),
        ('professional', 'Professional')
    ], default='vocabulary')
    estimated_duration = serializers.IntegerField(default=10)
    order = serializers.IntegerField(default=1)