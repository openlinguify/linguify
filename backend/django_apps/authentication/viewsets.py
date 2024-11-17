# backend/django_apps/authentication/viewsets.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from decimal import Decimal
from .models import CoachProfile
from .utils import notify_coach_of_commission_change
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer

class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ('patch', 'get')
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.exclude(is_superuser=True)

    def get_object(self):
        obj=User.objects.get_object_by_public_id(self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

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
        user = self.get_object()
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
