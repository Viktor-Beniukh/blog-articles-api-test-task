from rest_framework import serializers

from articles.models import Article
from users.serializers import UserSerializer


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)

    class Meta:
        model = Article
        fields = ("title", "content", "user")


class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="full_name", read_only=True)

    class Meta:
        model = Article
        fields = ("id", "title", "content", "picture", "published_at", "user")


class ArticleDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ("id", "title", "content", "picture", "published_at", "user")


class ArticlePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ("id", "picture")
