# app_manager/serializers.py
from rest_framework import serializers

class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ['id', 'name', 'display_name', 'description', 'icon_name']

class UserSubscriptionSerializer(serializers.ModelSerializer):
    selected_app = AppSerializer(read_only=True)
    has_access_to_all_apps = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserSubscription
        fields = ['id', 'subscription_type', 'selected_app', 'is_active', 'has_access_to_all_apps', 'premium_expiry']
