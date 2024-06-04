from django.contrib.auth import get_user_model
from django.test import TestCase

from users.models import Profile


class ModelsTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="admin@user.com",
            password="admin12345",
            username="Admin",
            first_name="John",
            last_name="Doe"
        )

    def test_user_str(self) -> None:
        expected_str = self.user.email

        self.assertEqual(str(self.user), expected_str)

    def test_user_full_name_property(self) -> None:
        expected_full_name = f"{self.user.first_name} {self.user.last_name}"

        self.assertEqual(self.user.full_name, expected_full_name)

    def test_profile_str(self) -> None:
        profile = Profile.objects.create(
            user=self.user,
        )
        self.assertEqual(str(profile), str(profile.user))
