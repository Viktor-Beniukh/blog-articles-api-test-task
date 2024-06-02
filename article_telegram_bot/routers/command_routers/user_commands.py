from aiogram import Router, types
from aiogram.filters import Command
from asgiref.sync import sync_to_async

from articles.models import Article

router = Router(name=__name__)


@sync_to_async
def get_latest_article():
    manual_article = Article.objects.filter(source="Manual").select_related("user").order_by("-id").first()

    scraped_article = Article.objects.filter(source="Scraped").order_by("-id").first()

    if manual_article and scraped_article:
        if manual_article.id > scraped_article.id:
            latest_article = manual_article
        else:
            latest_article = scraped_article
    elif manual_article:
        latest_article = manual_article
    elif scraped_article:
        latest_article = scraped_article
    else:
        return "There are no articles published yet."

    return (f"The latest published article: \n<b>#{latest_article.id}</b>. "
            f"<b>{latest_article.scraped_title if latest_article.source == 'Scraped' else latest_article.title}</b>"
            )


@router.message(Command("latest"))
async def send_latest_article(message: types.Message):
    latest_article = await get_latest_article()
    await message.answer(text=latest_article)
