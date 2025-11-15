from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.models import Category, Product
from sqlalchemy.orm import Session

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# ✅ YANGI: Asosiy kategoriyalar (Reply Keyboard)
def get_main_categories_keyboard(db):
    categories = db.query(Category).filter(
        Category.parent_id == None,
        Category.is_active == True
    ).all()
    
    keyboard = []
    row = []
    
    for category in categories:
        row.append(KeyboardButton(text=category.name))
        if len(row) == 2:  # Har qatorda 2 ta tugma
            keyboard.append(row)
            row = []
    
    if row:  # Qolgan tugmalar
        keyboard.append(row)
    
    # Asosiy menyuga qaytish
    keyboard.append([KeyboardButton(text="🏠 Asosiy menyu")])
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ✅ YANGI: Subkategoriyalar (Reply Keyboard)
def get_subcategories_keyboard(db, parent_id):
    subcategories = db.query(Category).filter(
        Category.parent_id == parent_id,
        Category.is_active == True
    ).all()
    
    keyboard = []
    row = []
    
    for subcategory in subcategories:
        row.append(KeyboardButton(text=subcategory.name))
        if len(row) == 2:  # Har qatorda 2 ta tugma
            keyboard.append(row)
            row = []
    
    if row:  # Qolgan tugmalar
        keyboard.append(row)
    
    # Navigatsiya tugmalari
    keyboard.append([
        KeyboardButton(text="◀️ Orqaga"),
        KeyboardButton(text="🏠 Asosiy menyu")
    ])
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ✅ YANGILANGAN: Mahsulotlar (Inline Keyboard) - HAR BIR MAHSULOT UCHUN ALOHIDA
def get_products_keyboard(products, category_id):
    """
    Har bir mahsulot uchun alohida 'Tanlash' tugmasi yaratadi
    """
    keyboard = []
    
    for product in products:
        # Har bir mahsulot uchun alohida "Tanlash" tugmasi
        keyboard.append([InlineKeyboardButton(
            text=f"🛒 Tanlash (ID: {product.id})",
            callback_data=f"product_{product.id}"
        )])
    
    # Orqaga qaytish tugmasi (subkategoriyaga qaytish)
    keyboard.append([InlineKeyboardButton(
        text="◀️ Orqaga (bo'limlar ro'yxati)",
        callback_data=f"back_category_{category_id}"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ✅ YANGI: Rang tanlash (Inline Keyboard)
def get_color_selection_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🟥 Qizil", callback_data="color_red"),
                InlineKeyboardButton(text="🟦 Ko'k", callback_data="color_blue"),
                InlineKeyboardButton(text="🟩 Yashil", callback_data="color_green")
            ],
            [
                InlineKeyboardButton(text="⬜ Oq", callback_data="color_white"),
                InlineKeyboardButton(text="⬛ Qora", callback_data="color_black"),
                InlineKeyboardButton(text="🟨 Sariq", callback_data="color_yellow")
            ],
            [
                InlineKeyboardButton(text="✏️ Boshqa rang", callback_data="color_custom"),
                InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_main")
            ]
        ]
    )

# ✅ YANGI: Razmer tanlash (Inline Keyboard)
def get_size_selection_keyboard():
    keyboard = []
    sizes = ["36", "37", "38", "39", "40", "41", "42", "43"]
    
    row = []
    for size in sizes:
        row.append(InlineKeyboardButton(text=size, callback_data=f"size_{size}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([
        InlineKeyboardButton(text="✏️ Boshqa razmer", callback_data="size_custom"),
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ✅ ESKI FUNKSIYALARNI SAQLAB QO'YAMIZ (Admin uchun kerak bo'lishi mumkin)
def get_categories_keyboard(db, parent_id=None):
    """Eski funksiya - admin paneli uchun saqlab qo'yamiz"""
    categories = db.query(Category).filter(
        Category.parent_id == parent_id,
        Category.is_active == True
    ).all()
    
    keyboard = []
    for category in categories:
        keyboard.append([InlineKeyboardButton(
            text=category.name,
            callback_data=f"category_{category.id}"
        )])
    
    if parent_id:
        parent_category = db.query(Category).filter(Category.id == parent_id).first()
        if parent_category and parent_category.parent_id:
            keyboard.append([InlineKeyboardButton(
                text="◀️ Orqaga",
                callback_data=f"category_{parent_category.parent_id}"
            )])
        else:
            keyboard.append([InlineKeyboardButton(
                text="◀️ Asosiy menyu",
                callback_data="back_to_main"
            )])
    else:
        keyboard.append([InlineKeyboardButton(
            text="◀️ Asosiy menyu",
            callback_data="back_to_main"
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)