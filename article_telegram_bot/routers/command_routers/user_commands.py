from aiogram import Router, types
from aiogram.filters import Command


router = Router(name=__name__)


def get_latest_article():
    return "Here is the latest article from the blog: [Link to the latest article]"


@router.message(Command("latest"))
async def send_latest_article(message: types.Message):
    latest_article = get_latest_article()
    await message.answer(text=latest_article)
