import os
import asyncio
import logging
import sys
import django

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from django.conf import settings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog_service.settings")
django.setup()

from article_telegram_bot.telegram_utils import send_message_to_chat
from article_telegram_bot.start_commands_list.start_cmd_list import start_commands
from article_telegram_bot.routers import router as main_router


BOT_TOKEN = settings.BOT_TOKEN
CHAT_ID = settings.TELEGRAM_CHAT_ID


async def main():
    dp = Dispatcher()
    dp.include_router(router=main_router)

    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)

    await send_message_to_chat(chat_id=int(CHAT_ID), message="Bot is starting...", bot=bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=start_commands, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
