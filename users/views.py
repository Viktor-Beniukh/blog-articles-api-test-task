from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from users.models import Profile
from users.serializers import (
    UserSerializer,
    ProfileSerializer,
    AuthTokenSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from users.utils import send_password_reset_email


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_user_model().objects.select_related("profile").get(pk=self.request.user.pk)


class CreateProfileView(generics.CreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({"message": "Your image already exists"})


class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)


class LogoutView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()
        return Response(
            {"message": "You have logged out successfully!"}, status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(generics.CreateAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data["email"]
            try:
                user = get_user_model().objects.get(email=email)
            except get_user_model().DoesNotExist:
                return Response(
                    {"detail": "User with this email does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            send_password_reset_email(user, request)

            return Response(
                {"detail": "Password reset link has been sent to your email address."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.UpdateAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_password = serializer.validated_data["new_password"]
            confirmed_password = serializer.validated_data["confirmed_password"]

            if new_password != confirmed_password:
                return Response(
                    {"detail": "New password and confirmed password do not match."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            uidb64 = kwargs.get("uidb64")
            token = kwargs.get("token")

            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = get_user_model().objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
                return Response(
                    {"detail": "Invalid UID or token."}, status=status.HTTP_400_BAD_REQUEST,
                )

            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response(
                    {"detail": "Password reset successfully."}, status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"detail": "Invalid UID or token."}, status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
