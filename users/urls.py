from django.urls import path

from users.views import (
    CreateUserView,
    LoginUserView,
    ManageUserView,
    CreateProfileView,
    UpdateProfileView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

app_name = "users"


urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", LoginUserView.as_view(), name="token"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "password/reset/request/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password/reset/confirm/<str:uidb64>/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("me/profile-create/", CreateProfileView.as_view(), name="profile-create"),
    path(
        "me/<int:pk>/profile-update/",
        UpdateProfileView.as_view(),
        name="profile-update",
    ),
]
