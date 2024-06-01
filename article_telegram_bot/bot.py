import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

from dotenv import load_dotenv

from telegram_utils import send_message_to_chat
from start_commands_list.start_cmd_list import start_commands
from routers import router as main_router

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


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
