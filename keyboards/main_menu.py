from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🛍 Kategoriya"), 
                KeyboardButton(text="🛒 Savat")
            ],
            [
                KeyboardButton(text="ℹ️ Ma'lumot"), 
                KeyboardButton(text="📞 Aloqa")
            ]
        ],
        resize_keyboard=True
    )

def get_subscription_check_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url="https://t.me/lino_wear_official")],
            [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription")]
        ]
    )