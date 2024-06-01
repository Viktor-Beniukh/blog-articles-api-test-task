import logging

from telebot import TeleBot
from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task
def send_new_article_notification_task(
    article_id: int, article_title: str, bot_token: str, chat_id: int
) -> None:
    bot = TeleBot(token=bot_token)
    message = f"New article published: \n\n#{article_id}. {article_title}"
    bot.send_message(chat_id=chat_id, text=message)
