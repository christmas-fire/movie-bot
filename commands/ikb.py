from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def ikb_start() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        InlineKeyboardButton(text="🚀 Добавить фильм", callback_data="add_movie")
    )
    builder.row(
        InlineKeyboardButton(text="🛠 Написать в поддержку", callback_data="help")
    )
    return builder.as_markup()


def ikb_profile() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📺 Мои фильмы", callback_data="my_movies"),
        InlineKeyboardButton(text="📈 Статистика", callback_data="statistic")
    )
    builder.row(
        InlineKeyboardButton(text="< Назад", callback_data="back_to_main_menu"),
    )
    return builder.as_markup()


def ikb_callback_my_movies() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Добавить в просмотренное", callback_data="add_viewed")
    )
    builder.row(
        InlineKeyboardButton(text="Добавить/обновить оценку", callback_data="update_rating")
    )
    builder.row(
        InlineKeyboardButton(text="< Назад", callback_data="back_to_profile")
    )
    return builder.as_markup()


def ikb_back_from_statistics() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="< Назад", callback_data="back_from_statistics")
    )
    return builder.as_markup()



def ikb_back() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="< Назад", callback_data="back_to_main_menu"),
    )
    return builder.as_markup()
