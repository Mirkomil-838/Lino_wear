from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_cart_keyboard(cart_items):
    keyboard = []
    for item in cart_items:
        keyboard.append([InlineKeyboardButton(
            text=f"❌ ID:{item.product.id} {item.product.name} ({item.color}, {item.size})",
            callback_data=f"remove_{item.id}"
        )])
    
    if cart_items:
        keyboard.append([InlineKeyboardButton(
            text="🛒 Buyurtma berish",
            callback_data="place_order"
        )])
    
    keyboard.append([InlineKeyboardButton(
        text="◀️ Asosiy menyu",
        callback_data="main_menu"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_location_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_payment_types_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Naqd"),
                KeyboardButton(text="Click")
            ],
            [
                KeyboardButton(text="Payme"),
                KeyboardButton(text="Bank kartasi")
            ],
            [
                KeyboardButton(text="◀️ Ortga")
            ]
        ],
        resize_keyboard=True
    )

# ✅ Yangi: Buyurtmani tasdiqlash keyboardi - YANA ANIQROQ
def get_order_confirmation_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ HA, Tasdiqlayman", callback_data="confirm_order"),
                InlineKeyboardButton(text="❌ Yo'q, Bekor qilish", callback_data="cancel_order")
            ]
        ]
    )