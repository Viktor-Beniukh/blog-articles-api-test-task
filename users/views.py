from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from drf_spectacular.utils import extend_schema, extend_schema_view

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


@extend_schema_view(
    post=extend_schema(
        description="Create a new user",
        request=UserSerializer,
        responses={201: UserSerializer},
    ),
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


@extend_schema_view(
    post=extend_schema(
        description="Logining existing user and receiving a token authorisation",
        request=AuthTokenSerializer,
        responses={200: AuthTokenSerializer},
    ),
)
class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


@extend_schema_view(
    get=extend_schema(
        description="Retrieve the specific user data",
        responses={200: UserSerializer},
    ),
    patch=extend_schema(
        description="Partially update the specific user data",
        request=UserSerializer,
        responses={200: UserSerializer},
    ),
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    http_method_names = ["get", "patch"]

    def get_object(self):
        return (
            get_user_model()
            .objects.select_related("profile")
            .get(pk=self.request.user.pk)
        )


@extend_schema_view(
    post=extend_schema(
        description="Create a new profile for the current user",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "format": "binary",
                    },
                },
                "required": ["image"],
            }
        },
        responses={
            201: ProfileSerializer,
        },
    )
)
class CreateProfileView(generics.CreateAPIView):
    serializer_class = ProfileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except IntegrityError:
            raise ValidationError({"message": "Your image already exists"})


@extend_schema_view(
    put=extend_schema(
        description="Update the existing profile for the current user",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "format": "binary",
                    },
                },
                "required": ["image"],
            }
        },
        responses={
            200: ProfileSerializer,
        },
    )
)
class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    http_method_names = ["put"]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)


@extend_schema_view(
    post=extend_schema(
        description="Logout user from the system",
        request=None,
        responses={
            200: {
                "description": "User has logged out successfully",
                "content": {
                    "application/json": {
                        "example": {"detail": "You have logged out successfully!"}
                    }
                },
            },
            401: {
                "description": "Error: Unauthorized",
                "content": {
                    "application/json": {
                        "examples": {
                            "authentication_error": {
                                "detail": "Authentication credentials were not provided."
                            },
                            "invalid_authentication_token": {
                                "detail": "Invalid token."
                            },
                        }
                    }
                },
            },
        },
    ),
)
class LogoutView(APIView):
    serializer_class = None
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()
        return Response(
            {"message": "You have logged out successfully!"},
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    post=extend_schema(
        description="Request password reset for the user",
        request=PasswordResetRequestSerializer,
        responses={
            200: {
                "description": "Password reset link has been sent to your email address.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Password reset link has been sent to your email address."
                        }
                    }
                },
            },
            400: {
                "description": "Validation error.",
                "content": {
                    "application/json": {
                        "example": {"email": ["This field is required."]}
                    }
                },
            },
            404: {
                "description": "User with this email does not exist.",
                "content": {
                    "application/json": {
                        "example": {"detail": "User with this email does not exist."}
                    }
                },
            },
        },
    ),
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
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    put=extend_schema(
        description="Confirm password reset for the user",
        request=PasswordResetConfirmSerializer,
        responses={
            200: {
                "description": "Password reset successfully.",
                "content": {
                    "application/json": {
                        "example": {"detail": "Password reset successfully."}
                    }
                },
            },
            400: {
                "description": "Validation error or invalid UID/token.",
                "content": {
                    "application/json": {
                        "examples": {
                            "validation_error": {
                                "detail": "New password and confirmed password do not match."
                            },
                            "invalid_uid_token": {"detail": "Invalid UID or token."},
                        }
                    }
                },
            },
        },
    )
)
class PasswordResetConfirmView(generics.UpdateAPIView):
    serializer_class = PasswordResetConfirmSerializer
    http_method_names = ["put"]

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
            except (
                TypeError,
                ValueError,
                OverflowError,
                get_user_model().DoesNotExist,
            ):
                return Response(
                    {"detail": "Invalid UID or token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response(
                    {"detail": "Password reset successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"detail": "Invalid UID or token."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
