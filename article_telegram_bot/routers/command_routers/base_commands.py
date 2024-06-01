from aiogram import Router, types
from aiogram.filters import CommandStart, Command


router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: types.Message):
    text = f"Hello, {message.from_user.full_name}! Welcome to The Blog Articles."
    await message.answer(text=text)


@router.message(Command("help"))
async def handle_help(message: types.Message):
    help_text = (
        "/start - Welcome message.\n"
        "/latest - Get the latest article from the blog."
    )
    await message.answer(text=help_text)
