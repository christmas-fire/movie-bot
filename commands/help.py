import os
from dotenv import load_dotenv

from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.utils.text_decorations import html_decoration

from database.users import get_user_by_user_id

from utils.text import text_start
from utils.kb import kb_cancel

from commands.ikb import ikb_start

help_router = Router()

load_dotenv()
ADMIN = int(os.getenv("ADMIN"))

class Help(StatesGroup):
    waiting_for_message = State()


@help_router.message(Command(commands=["help"]))
async def command_help(message: Message, state: FSMContext) -> None:
    text = (
        "Привет! 👋🏻\n\n"
        "Отправьте в этот чат свое сообщение, и оно будет переслано разработчику 🔧"
    )
    
    await message.answer(
        text=text,
        reply_markup=kb_cancel()
    )
    
    await state.set_state(Help.waiting_for_message)
    
    
@help_router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.delete()
    text = (
        "Привет! 👋🏻\n\n"
        "Отправьте в этот чат свое сообщение, и оно будет переслано разработчику 🔧"
    )
    
    await callback.message.answer(
        text=text,
        reply_markup=kb_cancel()
    )
    
    await state.set_state(Help.waiting_for_message)
    await callback.answer()
    

@help_router.message(StateFilter(Help.waiting_for_message))
async def callback_help_process(message: Message, bot: Bot, state: FSMContext) -> None:
    if message.text == "Отменить":
        await message.answer(
            text="Действие успешно отменено",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            text=text_start(first_name=message.from_user.first_name),
            reply_markup=ikb_start()
        )
        await state.clear()
        return
    
    try:
        text = message.text
        entities = message.entities
        decorated_text = html_decoration.unparse(text, entities)
        
        user = await get_user_by_user_id(user_id=message.from_user.id)
        await bot.send_message(
            chat_id=ADMIN,
            text=(
                f"📦 Пользователь <b>{user.first_name}</b> @{user.username} - <code>{user.user_id}</code> отправил вам сообщение:\n\n"
                f"<blockquote>{decorated_text}</blockquote>"
            )
        )
        
        await message.answer(
            text="🎉 Ваше сообщение передано в поддержку"
        )
        
        await message.answer(
            text=text_start(first_name=message.from_user.first_name),
            reply_markup=ikb_start()
        )
        await state.clear()
        
    except Exception:
        await message.answer(
            text="❌ Произошла ошибка, попробуйте позже"
        )
