from aiogram import Bot, types

async def set_bot_commands(bot: Bot):
    commands = [
        types.BotCommand(command="start", description="Запустить бота 🏁"),
        types.BotCommand(command="profile", description="Перейти в профиль 👤"),
        types.BotCommand(command="my_movies", description="Посмотреть мои фильмы 📺"),
        types.BotCommand(command="add_movie", description="Добавить фильм 🚀"),
        types.BotCommand(command="statistics", description="Посмотреть статистику 📈"),
        types.BotCommand(command="help", description="Написать в поддержку 🛠")
    ]
    await bot.set_my_commands(commands=commands, scope=types.BotCommandScopeAllPrivateChats())
