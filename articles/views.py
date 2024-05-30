from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from articles.models import Article
from articles.pagination import ApiPagination
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
    pagination_class = ApiPagination

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

    @extend_schema(
        methods=["POST"],
        description="Upload picture to specific article",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "picture": {
                        "type": "string",
                        "format": "binary",
                    },
                },
                "required": ["picture"],
            }
        },
        responses={
            200: ArticlePictureSerializer,
        },
    )
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=OpenApiTypes.STR,
                description="Filter by title (ex. ?title=python)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of articles"""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Retrieve a specific article",
        responses={200: ArticleDetailSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific article"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Create a new article",
        request=ArticleSerializer,
        responses={201: ArticleSerializer},
    )
    def create(self, request, *args, **kwargs):
        """Create a new article"""
        return super().create(request, *args, **kwargs)

    @extend_schema(
        description="Update an existing article",
        request=ArticleSerializer,
        responses={200: ArticleSerializer},
    )
    def update(self, request, *args, **kwargs):
        """Update an existing article"""
        return super().update(request, *args, **kwargs)

    @extend_schema(
        description="Partially update an existing article",
        request=ArticleSerializer,
        responses={200: ArticleSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update an existing article"""
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        description="Delete an existing article",
        responses={204: None},
    )
    def destroy(self, request, *args, **kwargs):
        """Delete an existing article"""
        return super().destroy(request, *args, **kwargs)
