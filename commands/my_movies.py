from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from database.movies import (
    get_movies_by_user, update_movie_as_watched, update_movie_rating,
    get_unwatched_movies, get_watched_movies, get_movie_by_title
)

from utils.movies import format_movie
from utils.text import text_start
from utils.kb import kb_cancel

from commands.ikb import ikb_start, ikb_back, ikb_callback_my_movies

my_movies_router = Router()

class AddViewed(StatesGroup):
    waiting_for_title = State()
    waiting_for_rating = State()
    
    
class UpdateRating(StatesGroup):
    waiting_for_title = State()
    waiting_for_rating = State()
    

@my_movies_router.message(Command(commands=["my_movies"]))
async def command_my_movies(message: Message) -> None:
    text = "<blockquote>📺 Мои фильмы</blockquote>\n\n"
    try:
        movies = await get_movies_by_user(added_by=str(message.from_user.id))
        for num, movie in enumerate(movies):
            text += f"{num+1}. "
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
        reply_markup=ikb_callback_my_movies()
    )
    

@my_movies_router.callback_query(F.data == "my_movies")
async def callback_my_movies(callback: CallbackQuery) -> None:
    text = "<blockquote>📺 Мои фильмы</blockquote>\n\n"
    try:
        movies = await get_movies_by_user(added_by=str(callback.from_user.id))
        for num, movie in enumerate(movies):
            text += f"{num+1}. "
            text += format_movie(title=movie.title,
                                 added_at=movie.added_at,
                                 is_watched=movie.is_watched,
                                 watched_at=movie.watched_at,
                                 rating=movie.rating
                                 )
            text += "\n"
            
    except Exception:
        await callback.message.edit_text(
            text="❌ Произошла ошибка, попробуйте позже",
            reply_markup=ikb_back()
        )
        
    await callback.message.edit_text(
        text=text,
        reply_markup=ikb_callback_my_movies()
    )
    

@my_movies_router.callback_query(StateFilter(None), F.data == "update_rating")
async def callback_update_rating(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.delete()
 
    text = "<blockquote>📺 Мои фильмы</blockquote>\n\n"
    
    movies = await get_watched_movies(added_by=str(callback.from_user.id))
    for num, movie in enumerate(movies):
        text += f"{num+1}. <code>{movie.title}</code> {"(" + str(movie.rating) + ")" if movie.rating != None else "(без оценки)"}\n"
    text +="\n<i>Введите название фильма (можете нажать на название и оно скопируется в буфер обмена)</i>"
        
    await callback.message.answer(
        text=text,
        reply_markup=kb_cancel()
    )
    
    await state.set_state(UpdateRating.waiting_for_title)
    await callback.answer() 

    
@my_movies_router.message(StateFilter(UpdateRating.waiting_for_title))
async def update_rating_process_title(message: Message, state: FSMContext) -> None:
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
        movie = await get_movie_by_title(added_by=str(message.from_user.id), title=message.text)
        if not movie:
            await message.answer(
                text=f"❌ Фильм не найден в вашем списке ожидания",
                reply_markup=kb_cancel()
            )
            return
        
        await state.update_data(title=message.text)
        await message.answer(
            text="Отлично! Теперь введите оценку (от 1 до 10)",
            reply_markup=kb_cancel()
        )
        await state.set_state(UpdateRating.waiting_for_rating)

    except Exception:
        await message.answer(
            text="❌ Произошла ошибка, попробуйте позже"
        )

    
@my_movies_router.message(StateFilter(UpdateRating.waiting_for_rating))
async def update_rating_process_raiting(message: Message, state: FSMContext) -> None:
    user_input = message.text
    rating = None
    
    if user_input == "Отменить":
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
        
    normalized_input = user_input.strip().replace(',', '.')
    rating_value = float(normalized_input)
    if not (1.0 <= rating_value <= 10.0):
        await message.answer(
            text="⚠️ Некорректный ввод. \nПожалуйста, введите оценку (от 1 до 10)",
            reply_markup=kb_cancel()
        )  
        return
    rating = rating_value
        
    data = await state.get_data()
    title = data.get('title')
    added_by = str(message.from_user.id)
    
    try:
        success = await update_movie_rating(
            added_by=added_by,
            title=title,
            rating=rating
        )
        
        if success:
            await message.answer(
                text=f"🎉 Оценка успешно обновлена",
                reply_markup=ReplyKeyboardRemove()
            )
        
    except Exception as e:
        print(f"Ошибка при обновлении фильма: {e}")
        await message.answer(
            text="Произошла ошибка при обновлении статуса фильма. Попробуйте позже",
            reply_markup=ReplyKeyboardRemove()
        )
        
    await state.clear()
    await message.answer(
        text=text_start(first_name=message.from_user.first_name),
        reply_markup=ikb_start()
    )
    
    
@my_movies_router.callback_query(StateFilter(None), F.data == "add_viewed")
async def callback_add_viewed(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.delete()
    
    text = "<blockquote>📺 Мои фильмы</blockquote>\n\n"
    
    movies = await get_unwatched_movies(added_by=str(callback.from_user.id))
    for num, movie in enumerate(movies):
        text += f"{num+1}. <code>{movie.title}</code> (не просмотрен)\n"
    text +="\n<i>Введите название фильма (можете нажать на название и оно скопируется в буфер обмена)</i>"
        
    await callback.message.answer(
        text=text,
        reply_markup=kb_cancel()
    )
    
    await state.set_state(AddViewed.waiting_for_title)
    await callback.answer()

    
@my_movies_router.message(StateFilter(AddViewed.waiting_for_title))
async def add_viewed_process_title(message: Message, state: FSMContext) -> None:
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
        movie = await get_movie_by_title(added_by=str(message.from_user.id), title=message.text)
        if not movie:
            await message.answer(
                text=f"❌ Фильм не найден в вашем списке ожидания",
                reply_markup=kb_cancel()
            )
            return
        
        await state.update_data(title=message.text)
    
        builder = ReplyKeyboardBuilder()
        builder.row(
            KeyboardButton(text="Пропустить")
        )
        builder.row(
            KeyboardButton(text="Отменить")
        )
        
        await message.answer(
            text="Отлично! Теперь введите оценку (от 1 до 10) или нажмите <b>Пропустить</b>",
            reply_markup=builder.as_markup(resize_keyboard=True)
        )
        await state.set_state(AddViewed.waiting_for_rating)
        
    except Exception:
        await message.answer(
            text="❌ Произошла ошибка, попробуйте позже"
        )
   

@my_movies_router.message(StateFilter(AddViewed.waiting_for_rating))
async def add_viewed_process_raiting(message: Message, state: FSMContext) -> None:
    user_input = message.text
    rating = None
    
    if user_input == "Отменить":
        await message.answer(
            text="Действие успешно отменено",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            text=f"{message.from_user.first_name}, вы в главном меню:",
            reply_markup=ikb_start()
        )
        await state.clear()
        return
        
    if user_input == "Пропустить":
        rating = None
    
    else:
        normalized_input = user_input.strip().replace(',', '.')
        rating_value = float(normalized_input)
        if not (1.0 <= rating_value <= 10.0):
            await message.answer(
                text="⚠️ Некорректный ввод. \nПожалуйста, введите оценку (от 1 до 10) или нажмите <b>Пропустить</b>",
                reply_markup=kb_cancel()
            )  
            return
        rating = rating_value
        
    data = await state.get_data()
    title = data.get('title')
    added_by = str(message.from_user.id)
    
    try:
        success = await update_movie_as_watched(
            added_by=added_by,
            title=title,
            rating=rating
        )
        
        if success:
            await message.answer(
                text=f"🎉 Фильм успешно отмечен как просмотренный",
                reply_markup=ReplyKeyboardRemove()
            )
        
    except Exception as e:
        print(f"Ошибка при обновлении фильма: {e}")
        await message.answer(
            text="Произошла ошибка при обновлении статуса фильма. Попробуйте позже",
            reply_markup=ReplyKeyboardRemove()
        )
        
    await state.clear()
    await message.answer(
        text=text_start(first_name=message.from_user.first_name),
        reply_markup=ikb_start()
    )
    