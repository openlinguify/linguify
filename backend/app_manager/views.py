# backend/app_manager/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from app_manager.models import AppModule, UserAppAccess
from app_manager.serializers import AppModuleSerializer, UserAppAccessSerializer
from authentication.models import User

class AppManagerViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=['GET'])
    def available_apps(self, request):
        user_access = request.user.userappaccess
        apps = AppModule.objects.filter(is_active=True)
        
        return Response([{
            'id': app.id,
            'name': app.name,
            'display_name': app.display_name,
            'description': app.description,
            'icon_name': app.icon_name,
            'has_access': (
                user_access.is_premium or 
                user_access.free_selected_app == app
            ),
            'is_selected': user_access.free_selected_app == app
        } for app in apps])

    @action(detail=True, methods=['POST'])
    def select_free_app(self, request, pk=None):
        try:
            app = AppModule.objects.get(pk=pk)
            user_access = request.user.userappaccess
            
            if user_access.is_premium:
                return Response(
                    {"error": "Les utilisateurs premium ont accès à toutes les apps"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user_access.free_selected_app = app
            user_access.save()
            
            return Response({"status": "ok"})
            
        except AppModule.DoesNotExist:
            return Response(
                {"error": "App non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        

# app_manager/views.py
class AppManagerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def select_free_app(self, request):
        app_name = request.data.get('app_name')
        
        if not app_name:
            return Response({'error': 'Nom de l\'app requis'}, status=400)
        
        user_access = request.user.userappaccess
        if user_access.is_premium:
            return Response({'error': 'Les utilisateurs premium ont accès à toutes les apps'}, status=400)
            
        if app_name not in dict(AppInfo.APP_CHOICES):
            return Response({'error': 'App invalide'}, status=400)
            
        user_access.selected_free_app = app_name
        user_access.save()
        
        return Response({'status': 'ok', 'selected_app': app_name})

    @action(detail=False, methods=['post'])
    def subscribe_premium(self, request):
        user_access = request.user.userappaccess
        
        # Ici, ajoutez la logique de paiement
        # Si le paiement réussit :
        user_access.is_premium = True
        user_access.premium_expiry = datetime.now() + timedelta(days=30)
        user_access.selected_free_app = None  # Reset la sélection gratuite
        user_access.save()
        
        return Response({'status': 'premium_activated'})

    @action(detail=False, methods=['get'])
    def user_status(self, request):
        user_access = request.user.userappaccess
        apps = AppInfo.objects.filter(is_active=True)
        
        return Response({
            'is_premium': user_access.is_premium,
            'selected_free_app': user_access.selected_free_app,
            'premium_expiry': user_access.premium_expiry,
            'available_apps': [
                {
                    'name': app.app_name,
                    'display_name': app.display_name,
                    'description': app.description,
                    'icon': app.icon_name,
                    'has_access': user_access.has_access_to(app.app_name)
                } for app in apps
            ]
        })
    

# app_manager/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

class AppManagerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AppSerializer

    def get_queryset(self):
        return App.objects.filter(is_active=True)

    @action(detail=False, methods=['GET'])
    def user_apps(self, request):
        """Renvoie toutes les apps avec leur statut d'accès pour l'utilisateur"""
        user_sub, created = UserSubscription.objects.get_or_create(user=request.user)
        apps = self.get_queryset()
        
        apps_data = []
        for app in apps:
            app_data = AppSerializer(app).data
            app_data['has_access'] = user_sub.can_access_app(app.name)
            app_data['is_selected'] = user_sub.selected_app == app
            apps_data.append(app_data)
        
        return Response({
            'subscription': UserSubscriptionSerializer(user_sub).data,
            'apps': apps_data
        })

    @action(detail=True, methods=['POST'])
    def select_free_app(self, request, pk=None):
        """Sélectionne une app gratuite"""
        try:
            app = App.objects.get(pk=pk)
            user_sub = UserSubscription.objects.get_or_create(user=request.user)[0]

            if user_sub.has_access_to_all_apps:
                return Response({
                    "error": "Les utilisateurs premium ont déjà accès à toutes les apps"
                }, status=status.HTTP_400_BAD_REQUEST)

            user_sub.subscription_type = 'free'
            user_sub.selected_app = app
            user_sub.save()

            return Response(UserSubscriptionSerializer(user_sub).data)

        except App.DoesNotExist:
            return Response({
                "error": "Application non trouvée"
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['POST'])
    def subscribe_premium(self, request):
        """Souscrit à l'abonnement premium"""
        user_sub = UserSubscription.objects.get_or_create(user=request.user)[0]
        
        # Ici, vous ajouteriez la logique de paiement
        
        user_sub.subscription_type = 'premium'
        user_sub.premium_expiry = timezone.now() + timezone.timedelta(days=30)
        user_sub.selected_app = None  # Reset l'app gratuite
        user_sub.save()

        return Response(UserSubscriptionSerializer(user_sub).data)
