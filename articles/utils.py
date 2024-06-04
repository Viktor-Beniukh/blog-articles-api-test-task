import os
import uuid

from django.utils.text import slugify


def articles_picture_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/articles/", filename)
