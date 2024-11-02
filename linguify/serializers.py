from rest_framework import serializers
from .models import Courses_languages, Courses_languages_categories

class Courses_languages_categoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses_languages_categories
        fields = '__all__'

class Courses_languagesSerializer(serializers.ModelSerializer):
    category =  Courses_languages_categoriesSerializer(read_only=True)
    
    class Meta:
        model = Courses_languages
        fields = '__all__'

