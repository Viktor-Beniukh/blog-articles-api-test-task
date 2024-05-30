import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from articles.models import Article
from articles.serializers import ArticleListSerializer, ArticleDetailSerializer


ARTICLE_URL = reverse("articles:article-list")


def sample_article(user, **params):

    defaults = {
        "title": "Python",
        "user": user,
    }
    defaults.update(params)

    return Article.objects.create(**defaults)


def detail_url(article_id):
    return reverse("articles:article-detail", args=[article_id])


def picture_upload_url(article_id):
    """Return URL for recipe picture upload"""
    return reverse("articles:article-upload-picture", args=[article_id])


class UnauthenticatedArticleApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ARTICLE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedArticleApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
            username="testuser"
        )
        self.client.force_authenticate(self.user)

    def test_list_articles(self):
        sample_article(user=self.user)
        sample_article(user=self.user)

        other_user = get_user_model().objects.create_user(
            email="other@test.com",
            password="testpass",
            username="otheruser"
        )
        sample_article(user=other_user)

        response = self.client.get(ARTICLE_URL)

        articles = Article.objects.all()
        serializer = ArticleListSerializer(articles, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_articles_by_title(self):
        article1 = sample_article(title="Django", user=self.user)
        article2 = sample_article(title="Python", user=self.user)
        article3 = sample_article(title="FastAPI", user=self.user)

        response = self.client.get(ARTICLE_URL, {"title": "python"})

        serializer1 = ArticleListSerializer(article1)
        serializer2 = ArticleListSerializer(article2)
        serializer3 = ArticleListSerializer(article3)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.assertNotIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_retrieve_article_detail(self):
        article = sample_article(user=self.user)

        url = detail_url(article.id)
        response = self.client.get(url)

        serializer = ArticleDetailSerializer(article)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_article(self):

        payload = {
            "title": "Python Programming",
            "user": self.user,
        }

        response = self.client.post(ARTICLE_URL, payload)

        article = Article.objects.get(title=response.data["title"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(article, key))

    def test_update_article(self):
        article = sample_article(user=self.user)

        payload = {
            "title": "Django Framework",
            "content": "About Django Framework",
        }

        url = detail_url(article.id)
        response = self.client.put(url, payload)

        article.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for key in payload:
            self.assertEqual(payload[key], getattr(article, key))

    def test_partial_update_article(self):
        article = sample_article(user=self.user)

        payload = {
            "content": "About Python Programming",
        }

        url = detail_url(article.id)
        response = self.client.patch(url, payload)

        article.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in payload:
            self.assertEqual(payload[key], getattr(article, key))

    def test_delete_article(self):
        article = sample_article(user=self.user)

        url = detail_url(article.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ArticlePictureUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
            username="testuser"
        )
        self.client.force_authenticate(self.user)
        self.article = sample_article(user=self.user)

    def tearDown(self):
        self.article.picture.delete()

    def test_upload_picture_to_article(self):
        """Test uploading a picture to article"""
        url = picture_upload_url(self.article.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"picture": ntf}, format="multipart")

        self.article.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("picture", res.data)
        self.assertTrue(os.path.exists(self.article.picture.path))

    def test_upload_picture_bad_request(self):
        """Test uploading an invalid picture"""
        url = picture_upload_url(self.article.id)
        res = self.client.post(url, {"picture": "not picture"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_picture_to_article_list(self):
        url = ARTICLE_URL

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "Django Framework",
                    "picture": ntf,
                    "user": self.user,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        article = Article.objects.get(title="Django Framework")
        self.assertFalse(article.picture)

    def test_picture_url_is_shown_on_article_detail(self):
        url = picture_upload_url(self.article.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"picture": ntf}, format="multipart")

        res = self.client.get(detail_url(self.article.id))

        self.assertIn("picture", res.data)

    def test_picture_url_is_shown_on_article_list(self):
        url = picture_upload_url(self.article.id)

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"picture": ntf}, format="multipart")

        res = self.client.get(ARTICLE_URL)

        self.assertIn("picture", res.data[0].keys())
