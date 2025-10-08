from rest_framework import serializers
from .app_manager_serializers import AppSerializer
from ..models.app_manager_models import App, UserAppSettings

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
