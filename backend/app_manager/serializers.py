# app_manager/serializers.py
from rest_framework import serializers
from .models import App, UserAppSettings

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

class UserAppSettingsSerializer(serializers.ModelSerializer):
    """Serializer for UserAppSettings model"""
    enabled_apps = AppSerializer(many=True, read_only=True)
    enabled_app_codes = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = UserAppSettings
        fields = [
            'id', 'user', 'enabled_apps', 'enabled_app_codes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        enabled_app_codes = validated_data.pop('enabled_app_codes', None)
        
        if enabled_app_codes is not None:
            # Get the apps that should be enabled
            apps_to_enable = App.objects.filter(
                code__in=enabled_app_codes,
                is_enabled=True
            )
            instance.enabled_apps.set(apps_to_enable)
        
        return super().update(instance, validated_data)

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