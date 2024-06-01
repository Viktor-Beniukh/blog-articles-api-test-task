__all__ = ("router",)

from aiogram import Router

from .command_routers import router as commands_router

router = Router(name=__name__)

router.include_router(router=commands_router)
