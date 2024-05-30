from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers

from users.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="full_name", read_only=True)

    class Meta:
        model = Profile
        fields = ("user", "image",)


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("user", "image")


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileListSerializer(read_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "is_staff",
            "profile",
        )
        read_only_fields = ("id", "is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update the user, set the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(label=_("Token"), read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )

            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _("Must include 'email' and 'password'.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user

        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}, min_length=5
    )
    confirmed_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}, min_length=5
    )