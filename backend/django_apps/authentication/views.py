# django_apps/authentication/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, TokenSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        if user:
            token_serializer = TokenSerializer(user)
            return Response(token_serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class PasswordResetView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = PasswordResetTokenGenerator().make_token(user)
            reset_url = f"http://localhost:8000/reset-password/{token}/"
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_url}',
                'admin@linguify.com',
                [user.email],
                fail_silently=False,
            )
            return Response({'message': 'Password reset email sent.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)