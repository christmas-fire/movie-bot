from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from database.users import create_user

from utils.text import text_start

from commands.ikb import ikb_start

start_router = Router()

@start_router.message(Command(commands=["start"]))
async def command_start(message: Message) -> None:
    await message.answer(
        text=text_start(first_name=message.from_user.first_name),
        reply_markup=ikb_start()
    )
    
    await create_user(
        user_id=message.from_user.id,
        username=message.from_user.username, 
        first_name=message.from_user.first_name
    )
