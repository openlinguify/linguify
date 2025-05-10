# backend/apps/authentication/views_terms.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from .serializers import TermsAcceptanceSerializer


@extend_schema(
    tags=["Terms & Conditions"],
    summary="Accept terms and conditions",
    description="Endpoint for users to accept the terms and conditions",
    request=TermsAcceptanceSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"}
            }
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string"}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_terms(request):
    """
    Accept terms and conditions
    """
    # Add debugging info
    print(f"Accept terms request received from: {request.user.email if hasattr(request, 'user') and hasattr(request.user, 'email') else 'Unknown'}")
    print(f"Request data: {request.data}")

    serializer = TermsAcceptanceSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({
            "success": True,
            "message": "Terms and conditions accepted successfully"
        }, status=status.HTTP_200_OK)

    print(f"Terms acceptance validation errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Terms & Conditions"],
    summary="Get terms acceptance status",
    description="Get the current user's terms and conditions acceptance status",
    responses={
        200: {
            "type": "object",
            "properties": {
                "terms_accepted": {"type": "boolean"},
                "terms_accepted_at": {"type": "string", "format": "date-time", "nullable": True},
                "terms_version": {"type": "string", "nullable": True}
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def terms_status(request):
    """
    Get current terms acceptance status
    """
    user = request.user
    return Response({
        "terms_accepted": user.terms_accepted,
        "terms_accepted_at": user.terms_accepted_at,
        "terms_version": user.terms_version
    }, status=status.HTTP_200_OK)