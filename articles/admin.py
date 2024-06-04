from django.contrib import admin

from articles.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "published_at")
    list_filter = ("published_at",)
    search_fields = ("title", "published_at",)
