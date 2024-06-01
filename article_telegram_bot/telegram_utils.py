from aiogram import Bot


async def send_message_to_chat(chat_id: int, message: str, bot: Bot):
    await bot.send_message(chat_id=chat_id, text=message)
