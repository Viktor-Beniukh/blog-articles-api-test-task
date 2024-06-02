from django.urls import path, include
from rest_framework import routers

from articles.views import ArticleViewSet, ArticleScrapedViewSet

router = routers.DefaultRouter()
router.register("articles", ArticleViewSet)
router.register("scraped-articles", ArticleScrapedViewSet, basename="scraped-articles")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "articles"
