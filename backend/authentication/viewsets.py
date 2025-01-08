# backend/django_apps/authentication/viewsets.py
import jwt

from functools import wraps
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from decimal import Decimal
from .utils import notify_coach_of_commission_change
from .models import User, CoachProfile, Review, UserFeedback
from .serializers import UserSerializer, UserRegistrationSerializer, CoachProfileSerializer, ReviewSerializer, UserFeedbackSerializer


# API Scope-based permissions
# Source: https://auth0.com/docs/quickstart/backend/django/01-authorization
# Not sure we need this for now, but it's here for reference for later use

def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token

def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            decoded = jwt.decode(token, verify=False)
            if decoded.get("scope"):
                token_scopes = decoded["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            response = JsonResponse({'message': 'You don\'t have access to this resource'})
            response.status_code = 403
            return response
        return decorated
    return require_scope

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ('get', 'patch', 'post')
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.exclude(is_superuser=True)

    def get_object(self):
        try:
            obj=User.objects.get(public_id=self.kwargs['pk'])
            self.check_object_permissions(self.request, obj)
            return obj
        except User.DoesNotExist:
            raise PermissionDenied("User not found.")

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()  # Ici, self.get_object() utilise `pk` en interne
        if request.user != user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to deactivate this user.")
        user.deactivate_user()
        return Response({"message": "User deactivated successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        user = self.get_object()
        if request.user != user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to reactivate this user.")
        user.reactivate_user()
        return Response({"message": "User reactivated successfully."}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        # Ensuring sensitive fields are not modified
        sensitive_fields = ['email', 'is_superuser', 'is_staff', 'is_active']
        for field in sensitive_fields:
            if field in serializer.validated_data:
                serializer.validated_data.pop(field)
        serializer.save()


class UpdateCommissionOverride(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, coach_id):
        try:
            coach_profile = CoachProfile.objects.get(user__id=coach_id)
            commission_override = request.data.get('commission_override')

            if commission_override is not None:
                coach_profile.commission_override = Decimal(commission_override)
                coach_profile.save()
                notify_coach_of_commission_change(coach_profile)
                return Response({"message": "Commission override updated successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No commission override provided."}, status=status.HTTP_400_BAD_REQUEST)

        except CoachProfile.DoesNotExist:
            return Response({"error": "Coach profile not found."}, status=status.HTTP_404_NOT_FOUND)

# Vues pour le modèle CoachProfile
class CoachProfileViewSet(viewsets.ModelViewSet):
    queryset = CoachProfile.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CoachProfileSerializer

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_availability(self, request, pk=None):
        coach = self.get_object()
        availability = request.data.get('availability')
        if availability:
            coach.update_availability(availability)
            return Response({"message": "Availability updated successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "No availability provided."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_price(self, request, pk=None):
        coach = self.get_object()
        price = request.data.get('price_per_hour')
        if price:
            coach.update_price_per_hour(Decimal(price))
            return Response({"message": "Price updated successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "No price provided."}, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def create(self, request, *args, **kwargs):
        reviewer = request.user
        data = request.data.copy()
        data['reviewer'] = reviewer.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Vues pour le modèle UserFeedback
class UserFeedbackViewSet(viewsets.ModelViewSet):
    queryset = UserFeedback.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserFeedbackSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        data['user'] = user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
