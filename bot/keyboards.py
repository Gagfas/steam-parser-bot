from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои скины")],
            [KeyboardButton(text="➕ Добавить скин"), KeyboardButton(text="❌ Удалить")],
            [KeyboardButton(text="💰 Цена сейчас"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )
