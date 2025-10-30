from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def kb_admin() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="👥 Пользователи"),
    )
    builder.row(
        KeyboardButton(text="📺 Все фильмы"),
    )
    builder.row(
        KeyboardButton(text="✏️ Отправить сообщение")
    )
    return builder.as_markup(resize_keyboard=True)
