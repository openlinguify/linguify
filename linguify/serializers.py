from rest_framework import serializers
from .models import Courses_languages, Courses_languages_categories

class CoursesLanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses_languages
        fields = '__all__'

class CoursesLanguagesCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses_languages_categories
        fields = '__all__'
