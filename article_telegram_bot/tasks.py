import logging

from telebot import TeleBot
from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task
def send_new_article_notification_task(
    article_id: int, article_title: str, bot_token: str, chat_id: int
) -> None:
    bot = TeleBot(token=bot_token, parse_mode="HTML")
    message = f"New article published: \n\n<b>#{article_id}. {article_title}</b>"
    bot.send_message(chat_id=chat_id, text=message)
