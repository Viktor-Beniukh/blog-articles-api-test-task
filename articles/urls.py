from django.urls import path, include
from rest_framework import routers

from articles.views import ArticleViewSet

router = routers.DefaultRouter()
router.register("articles", ArticleViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "articles"
