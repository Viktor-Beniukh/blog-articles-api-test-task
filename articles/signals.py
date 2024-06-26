import logging
import re

from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from article_telegram_bot.tasks import send_new_article_notification_task

from .models import Article

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def send_new_article_notification(sender, instance, created, **kwargs):
    if created:
        if instance.source == "Manual":
            article_title = instance.title
        else:
            article_title = instance.scraped_title

        article_id = instance.id
        bot_token = settings.BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID

        logger.info(f"Article created: {article_title}. Sending notification.")
        send_new_article_notification_task.delay(
            article_id=article_id,
            article_title=article_title,
            bot_token=bot_token,
            chat_id=int(chat_id)
        )


@receiver(pre_save, sender=Article)
def prepend_base_url(sender, instance, **kwargs):
    if instance.scraped_url and not re.match(r"https?://", instance.scraped_url):
        base_url = "https://news.ycombinator.com/"
        instance.scraped_url = base_url + instance.scraped_url
