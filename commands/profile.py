from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database.users import get_user_by_user_id
from utils.text import text_start

from commands.ikb import ikb_start, ikb_profile

profile_router = Router()

class Purchase(StatesGroup):
    waiting_for_amount = State()


@profile_router.message(Command(commands=["profile"]))
async def command_profile(message: Message) -> None:
    try:
        user = await get_user_by_user_id(user_id=message.from_user.id)
        
        await message.answer(
            text=(
                f"<blockquote>👤 Профиль</blockquote>\n\n"
                f"ID - <code>{user.user_id}</code>\n"
f"Дата регистрации - <b>{user.created_at.strftime('%d.%m.%Y')}</b>"
            ),
            reply_markup= ikb_profile() 
        )
    except Exception:
        await message.answer(
            text="❌ Произошла ошибка, попробуйте позже"
        )
    

@profile_router.callback_query(F.data == "profile")
async def callback_profile(callback: CallbackQuery) -> None:
    try:
        user = await get_user_by_user_id(user_id=callback.from_user.id)
        
        await callback.message.edit_text(
            text=(
                f"<blockquote>👤 Профиль</blockquote>\n\n"
                f"ID - <code>{user.user_id}</code>\n"
f"Дата регистрации - <b>{user.created_at.strftime('%d.%m.%Y')}</b>"
            ),
            reply_markup= ikb_profile()
    )
    except Exception:
        await callback.message.answer(
            text="❌ Произошла ошибка, попробуйте позже"
        )
    await callback.answer()
        
        
@profile_router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    
    user = await get_user_by_user_id(user_id=callback.from_user.id)
    text = (
        f"<blockquote>👤 Профиль</blockquote>\n\n"
        f"ID - <code>{user.user_id}</code>\n"
        f"Дата регистрации - <b>{user.created_at.strftime('%d.%m.%Y')}</b>"
    )
    
    if callback.message.photo:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=ikb_profile()
        )
    else:
        await callback.message.edit_text(
            text=text,
            reply_markup=ikb_profile()
        )
    
    await callback.answer()


@profile_router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        text=text_start(first_name=callback.from_user.first_name),
        reply_markup=ikb_start()
    )
    await callback.answer()
