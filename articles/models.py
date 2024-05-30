from django.conf import settings
from django.db import models

from articles.utils import articles_picture_file_path


class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    picture = models.ImageField(upload_to=articles_picture_file_path, null=True)
    published_at = models.DateField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles"
    )

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title
