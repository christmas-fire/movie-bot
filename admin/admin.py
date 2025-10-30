import os
from dotenv import load_dotenv

from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.utils.text_decorations import html_decoration

from database.users import get_all_users, get_user_by_user_id
from database.movies import get_all_movies

from utils.movies import format_movie
from utils.kb import kb_cancel

from admin.kb import kb_admin

class AdminSendMessage(StatesGroup):
    waiting_for_id = State()
    waiting_for_message = State()


admin_router = Router()

load_dotenv()
ADMIN = int(os.getenv("ADMIN"))


@admin_router.message(Command(commands=["admin"]))
async def command_admin(message: Message) -> None:
    if message.from_user.id != ADMIN:
        await message.answer(
            text="⚠️ У вас недостаточно прав для этого действия"
        )
        return
    
    await message.answer(
        text="Добро пожаловать! 👋🏻",
        reply_markup=kb_admin()
    )


@admin_router.message(F.text == "👥 Пользователи")
async def admin_users(message: Message) -> None:
    await message.delete()
    text = "<blockquote>👥 Пользователи</blockquote>\n\n"
    try:
        users = await get_all_users()
        for user in users:
            text += f"{user.id}. <b>{user.first_name}</b> @{user.username} - <code>{user.user_id}</code>"
            text += "\n"
    except Exception:
        await message.answer(
            "❌ Произошла ошибка, попробуйте позже"
        )
        
    await message.answer(
        text=text
    )
    

@admin_router.message(F.text == "📺 Все фильмы")
async def admin_movies(message: Message) -> None:
    await message.delete()
    text = "<blockquote>📺 Все фильмы</blockquote>\n\n"
    try:
        movies = await get_all_movies()
        for num, movie in enumerate(movies):
            user = await get_user_by_user_id(user_id=int(movie.added_by))
            text += f"{num+1}. <b>{user.first_name}</b> @{user.username} - <code>{user.user_id}</code>\n"
            text += format_movie(title=movie.title,
                                 added_at=movie.added_at,
                                 is_watched=movie.is_watched,
                                 watched_at=movie.watched_at,
                                 rating=movie.rating
                                 )
            text += "\n"
            
    except Exception:
        await message.answer(
            "❌ Произошла ошибка, попробуйте позже"
        )
        
    await message.answer(
        text=text,
        reply_markup=kb_admin()
    )
            

@admin_router.message(StateFilter(None), F.text == "✏️ Отправить сообщение")
async def admin_send_message(message: Message, state: FSMContext) -> None:
    text = "<blockquote>👥 Пользователи</blockquote>\n\n"
    try:
        users = await get_all_users()
        for user in users:
            text += f"{user.id}. <b>{user.first_name}</b> @{user.username} - <code>{user.user_id}</code>"
            text += "\n"
            
    except Exception:
        await message.answer(
            "❌ Произошла ошибка, попробуйте позже"
        )
    
    text += "\n<i>Введите ID пользователя, которому вы хотите отправить сообщение</i>"
    await message.answer(
        text=text,
        reply_markup=kb_cancel()
    )
    
    await state.set_state(AdminSendMessage.waiting_for_id)
    
    
@admin_router.message(StateFilter(AdminSendMessage.waiting_for_id))
async def admin_send_message_process(message: Message, state: FSMContext) -> None:
    if message.text == "Отменить":
        await message.delete()
        await message.answer(
            text=f"Добро пожаловать! 👋🏻",
            reply_markup=kb_admin()
        )
        await state.clear()
        return
    
    user_id = message.text
    await state.update_data(user_id=user_id)
    
    await message.answer(
        text="Введите сообщение, которое получит пользователь",
        reply_markup=kb_cancel()
    )
    
    await state.set_state(AdminSendMessage.waiting_for_message)
    
    
@admin_router.message(StateFilter(AdminSendMessage.waiting_for_message))
async def admin_send_message_finish(message: Message, bot: Bot, state: FSMContext) -> None:
    if message.text == "Отменить":
        await message.delete()
        await message.answer(
            text=f"Добро пожаловать! 👋🏻",
            reply_markup=kb_admin()
        )
        await state.clear()
        return
    
    data = await state.get_data()
    user_id = data.get('user_id')
    
    text = message.text
    entities = message.entities
    decorated_text = html_decoration.unparse(text, entities)
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text=decorated_text
        )
        await message.answer(
            text=(
                "Сообщение успешно отправлено пользователю\n\n"
                f"<blockquote>{decorated_text}</blockquote>"
            ),
            reply_markup=kb_admin()
        )
        await state.clear()
        
    except Exception:
        await message.answer(f"⚠️ Ошибка отправки сообщения, попробуйте еще раз")
        return
    