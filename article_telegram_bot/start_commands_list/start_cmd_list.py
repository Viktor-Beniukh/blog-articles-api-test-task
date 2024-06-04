from aiogram.types import BotCommand


start_commands = [
    BotCommand(command="start", description="Welcome message"),
    BotCommand(command="help", description="list of available commands and their descriptions"),
    BotCommand(command="latest", description="Get the latest article from the blog"),
]
