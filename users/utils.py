import os
import uuid

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.text import slugify


def profile_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.user.username)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/profiles/", filename)


def send_password_reset_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    reset_password_url = reverse(
        "users:password-reset-confirm", kwargs={"uidb64": uid, "token": token}
    )
    reset_password_url = f"http://{request.get_host()}{reset_password_url}"

    subject = "Password Reset Request"
    message = render_to_string("password_reset_email.txt", {
        "user": user,
        "reset_password_url": reset_password_url
    })
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
