import asyncio
import os
import dotenv
import logging
import uvicorn

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from api.main import app

from database.init import create_pool
from database.users import create_users_table
from database.movies import create_movies_table
from default_commands import set_bot_commands

from commands.start import start_router
from commands.profile import profile_router
from commands.my_movies import my_movies_router
from commands.add_movie import add_movie_router
from commands.statistics import statistics_router
from commands.help import help_router

from admin.admin import admin_router

dotenv.load_dotenv()
TOKEN = os.getenv('TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

async def start_bot():
    await set_bot_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Starting bot polling...")
    await dp.start_polling(bot)

async def start_api():
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)
    logging.info("Starting API server...")
    await server.serve()

async def main():
    await create_pool()
    await create_users_table()
    await create_movies_table()
    
    dp.include_routers(
        start_router,
        profile_router,
        admin_router,
        my_movies_router,
        add_movie_router,
        statistics_router,
        help_router
    )

    await asyncio.gather(
        start_bot(),
        start_api()
    )

if __name__ == '__main__':
    logging.info(msg="start server")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info(msg="shutdown server")
