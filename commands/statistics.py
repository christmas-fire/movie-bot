from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.media_group import MediaGroupBuilder

from database.users import get_user_by_user_id

from utils.statistics import generate_movie_statistics

from commands.ikb import ikb_profile

statistics_router = Router()

class Purchase(StatesGroup):
    waiting_for_amount = State()


@statistics_router.message(Command(commands=["statistics"]))
async def command_profile(message: Message) -> None:
    text_report, ratings_plot_buffer, status_plot_buffer, rated_status_plot_buffer = await generate_movie_statistics(
        user_id=str(message.from_user.id)
    )
    
    album_builder = MediaGroupBuilder(
        caption=text_report
    )
    
    album_builder.add_photo(
        media=BufferedInputFile(status_plot_buffer.read(), filename="movie_status.png")
    )
    album_builder.add_photo(
        media=BufferedInputFile(rated_status_plot_buffer.read(), filename="rated_status.png")
    )
    album_builder.add_photo(
        media=BufferedInputFile(ratings_plot_buffer.read(), filename="movie_ratings.png")
    )
    
    await message.answer_media_group(
        media=album_builder.build()
    )
    

@statistics_router.callback_query(F.data == "statistic")
async def callback_statistic(callback: CallbackQuery) -> None:
    await callback.message.delete()   
    
    text_report, ratings_plot_buffer, status_plot_buffer, rated_status_plot_buffer = await generate_movie_statistics(
        user_id=str(callback.from_user.id)
    )
    
    album_builder = MediaGroupBuilder(
        caption=text_report
    )
    
    album_builder.add_photo(
        media=BufferedInputFile(status_plot_buffer.read(), filename="movie_status.png")
    )
    album_builder.add_photo(
        media=BufferedInputFile(rated_status_plot_buffer.read(), filename="rated_status.png")
    )
    album_builder.add_photo(
        media=BufferedInputFile(ratings_plot_buffer.read(), filename="movie_ratings.png")
    )
    
    await callback.message.answer_media_group(
        media=album_builder.build()
    )
    await callback.answer()    
    
    
@statistics_router.callback_query(F.data == "back_from_statistics")
async def callback_back_from_statistics(callback: CallbackQuery) -> None:
    await callback.message.delete()
    
    user = await get_user_by_user_id(user_id=callback.from_user.id)
    await callback.message.answer(
        text = (
            f"<blockquote>👤 Профиль</blockquote>\n\n"
            f"ID - <code>{user.user_id}</code>\n"
            f"Дата регистрации - <b>{user.created_at.strftime('%d.%m.%Y')}</b>"
        ),
        reply_markup=ikb_profile()
    )
