from aiogram import Router, types
from aiogram.filters import Command
from asgiref.sync import sync_to_async

from articles.models import Article

router = Router(name=__name__)


@sync_to_async
def get_latest_article():
    latest_article = Article.objects.select_related("user").order_by("-id").first()
    if latest_article:
        return f"The latest published article: \n#{latest_article.id}. {latest_article.title}"
    else:
        return "There are no articles published yet."


@router.message(Command("latest"))
async def send_latest_article(message: types.Message):
    latest_article = await get_latest_article()
    await message.answer(text=latest_article)
