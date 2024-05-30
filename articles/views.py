from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from articles.models import Article
from articles.permissions import IsAuthorOrReadOnly
from articles.serializers import (
    ArticleSerializer,
    ArticleListSerializer,
    ArticlePictureSerializer,
    ArticleDetailSerializer,
)


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.select_related("user")
    serializer_class = ArticleSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

    def get_queryset(self):
        """Retrieve the article with filter"""
        title = self.request.query_params.get("title")

        queryset = super().get_queryset()

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ArticleListSerializer

        if self.action == "retrieve":
            return ArticleDetailSerializer

        if self.action == "upload_picture":
            return ArticlePictureSerializer

        return super().get_serializer_class()

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-picture",
        permission_classes=[IsAuthenticated, IsAuthorOrReadOnly],
    )
    def upload_picture(self, request, pk=None):
        """Endpoint for uploading picture to specific article"""
        article = self.get_object()
        serializer = self.get_serializer(article, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
