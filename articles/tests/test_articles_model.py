from django.contrib.auth import get_user_model
from django.test import TestCase

from articles.models import Article


class ModelsTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="admin@user.com",
            password="admin12345",
            username="Admin",
        )

    def test_article_str(self) -> None:
        article = Article.objects.create(title="Django", user=self.user)

        self.assertEqual(str(article), article.title)
