import os

from django.conf import settings
from django.db import models

from PIL import Image

from articles.utils import articles_picture_file_path


class Article(models.Model):
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    picture = models.ImageField(upload_to=articles_picture_file_path, null=True)
    published_at = models.DateField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name="articles"
    )
    scraped_title = models.CharField(max_length=255, blank=True, null=True)
    scraped_url = models.URLField(max_length=2000, blank=True, null=True)

    class Meta:
        ordering = ["-published_at", "-id"]

    def __str__(self):
        return self.title

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
        *args,
        **kwargs,
    ):
        try:
            old_instance = Article.objects.get(pk=self.pk)
            old_picture = old_instance.picture
        except Article.DoesNotExist:
            old_picture = None

        super().save(*args, **kwargs)

        if old_picture and self.picture != old_picture:
            if os.path.isfile(old_picture.path):
                os.remove(old_picture.path)

        if self.picture:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.picture.path)
