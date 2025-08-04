# app_manager/serializers.py
from rest_framework import serializers
from ..models.app_manager_models import App

class AppSerializer(serializers.ModelSerializer):
    """Serializer for App model"""
    
    class Meta:
        model = App
        fields = [
            'id', 'code', 'display_name', 'description', 
            'icon_name', 'color', 'route_path', 'is_enabled', 
            'order', 'category', 'version', 'installable', 
            'manifest_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class AppToggleSerializer(serializers.Serializer):
    """Serializer for toggling app activation"""
    app_code = serializers.CharField()
    enabled = serializers.BooleanField()
    
    def validate_app_code(self, value):
        """Validate that the app exists and is enabled globally"""
        try:
            app = App.objects.get(code=value, is_enabled=True)
            return value
        except App.DoesNotExist:
            raise serializers.ValidationError("App not found or not available")