# app_manager/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import App, UserAppSettings
from .serializers import AppSerializer, UserAppSettingsSerializer, AppToggleSerializer

class AppListView(generics.ListAPIView):
    """
    List all available applications with deduplication
    """
    serializer_class = AppSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Get all enabled apps
        apps = App.objects.filter(is_enabled=True).order_by('display_name', '-id')
        
        # Deduplicate by display_name - keep the one with highest ID (most recent)
        seen_names = set()
        unique_apps = []
        
        for app in apps:
            if app.display_name not in seen_names:
                unique_apps.append(app)
                seen_names.add(app.display_name)
        
        # Return as queryset - we'll filter the IDs
        unique_ids = [app.id for app in unique_apps]
        return App.objects.filter(id__in=unique_ids).order_by('order', 'display_name')

class UserAppSettingsView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user app settings
    """
    serializer_class = UserAppSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        # Get or create user app settings
        user_settings, created = UserAppSettings.objects.get_or_create(
            user=self.request.user
        )
        
        # If newly created, enable all apps by default
        if created:
            all_apps = App.objects.filter(is_enabled=True)
            user_settings.enabled_apps.set(all_apps)
        
        return user_settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_app(request):
    """
    Toggle an app on/off for the current user
    """
    serializer = AppToggleSerializer(data=request.data)
    if serializer.is_valid():
        app_code = serializer.validated_data['app_code']
        enabled = serializer.validated_data['enabled']
        
        # Get or create user app settings
        user_settings, created = UserAppSettings.objects.get_or_create(
            user=request.user
        )
        
        if enabled:
            success = user_settings.enable_app(app_code)
            message = f"App '{app_code}' enabled successfully" if success else f"Failed to enable app '{app_code}'"
        else:
            success = user_settings.disable_app(app_code)
            message = f"App '{app_code}' disabled successfully" if success else f"Failed to disable app '{app_code}'"
        
        if success:
            return Response({
                'success': True,
                'message': message,
                'enabled_apps': user_settings.get_enabled_app_codes()
            })
        else:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_enabled_apps(request):
    """
    Get list of apps enabled for the current user
    """
    user_settings, created = UserAppSettings.objects.get_or_create(
        user=request.user
    )
    
    # If newly created, enable all apps by default
    if created:
        all_apps = App.objects.filter(is_enabled=True)
        user_settings.enabled_apps.set(all_apps)
    
    enabled_apps = user_settings.enabled_apps.filter(is_enabled=True)
    serializer = AppSerializer(enabled_apps, many=True)
    
    return Response({
        'enabled_apps': serializer.data,
        'enabled_app_codes': user_settings.get_enabled_app_codes()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_apps(request):
    """
    Debug view to see all app data
    """
    user_settings, created = UserAppSettings.objects.get_or_create(
        user=request.user
    )
    
    all_apps = App.objects.all().order_by('code')
    enabled_apps = user_settings.enabled_apps.all()
    
    app_data = []
    for app in all_apps:
        app_data.append({
            'id': app.id,
            'code': app.code,
            'display_name': app.display_name,
            'is_enabled': app.is_enabled,
            'user_has_enabled': app in enabled_apps
        })
    
    return Response({
        'total_apps': all_apps.count(),
        'enabled_by_user': enabled_apps.count(),
        'apps': app_data,
        'enabled_app_codes': user_settings.get_enabled_app_codes(),
        'user_created': created
    })