# backend/django_apps/authentication/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from decimal import Decimal
from .models import CoachProfile
from .utils import notify_coach_of_commission_change

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
