import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from users.models import Profile


PROFILE_URL = reverse("users:profile-create")
USER_URL = reverse("users:manage")


def image_upload_url():
    """Return URL for recipe image upload"""
    return reverse("users:profile-create")


class UnauthenticatedProfileApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedProfileApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass"
        )
        self.client.force_authenticate(self.user)

    def test_create_profile(self):
        payload = {
            "user": self.user.email,
        }

        response = self.client.post(PROFILE_URL, payload)

        profile = Profile.objects.get(user=self.user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(payload["user"], profile.user.email)


class ProfileImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
            username="testuser"
        )
        self.client.force_authenticate(self.user)

    def tearDown(self):
        profile = Profile.objects.filter(user=self.user).first()
        if profile and profile.image:
            profile.image.delete()

    def test_upload_image_to_profile(self):
        """Test uploading an image to user profile"""
        url = image_upload_url()

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")

        self.user.refresh_from_db()
        profile = self.user.profile

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(profile.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url()
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_image_url_is_shown_on_user_page(self):
        url = image_upload_url()

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        res = self.client.get(USER_URL)

        self.assertIn("image", res.data["profile"])
