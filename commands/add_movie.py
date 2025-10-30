from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from database.movies import create_movie

from utils.text import text_start
from utils.kb import kb_cancel

from commands.ikb import ikb_start

add_movie_router = Router()

class CreateMovie(StatesGroup):
    waiting_for_data = State()


@add_movie_router.message(Command(commands=["add_movie"]))
async def command_add_movie(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="Введите название фильма",
        reply_markup=kb_cancel()
    )
    
    await state.set_state(CreateMovie.waiting_for_data)


@add_movie_router.callback_query(StateFilter(None), F.data == "add_movie")
async def command_add_movie(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.delete()    
    await callback.message.answer(
        text="Введите название фильма",
        reply_markup=kb_cancel()
    )

    await state.set_state(CreateMovie.waiting_for_data)
    await callback.answer()
    
    
@add_movie_router.message(StateFilter(CreateMovie.waiting_for_data))
async def command_add_movie_process(message: Message, state: FSMContext) -> None:
    title = message.text
    added_by = str(message.from_user.id)
    
    if message.text == "Отменить":
        await message.delete()
        
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
        await create_movie(title=title, added_by=added_by)
        await message.answer(
            text=f"🎉 Фильм успешно добавлен",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            text=text_start(first_name=message.from_user.first_name),
            reply_markup=ikb_start()
        )
        await state.clear()
    except Exception:
        await message.answer(
            text="❌ Произошла ошибка, попробуйте позже",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            text=text_start(first_name=message.from_user.first_name),
            reply_markup=ikb_start()
        )
        await state.clear()
