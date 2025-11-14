from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database.models import Category
from sqlalchemy.orm import Session

def get_admin_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📦 Mahsulot qo'shish"), 
                KeyboardButton(text="📊 Statistika")
            ],
            [
                KeyboardButton(text="🏠 Asosiy menyu")
            ]
        ],
        resize_keyboard=True
    )

def get_categories_keyboard_admin(db: Session, parent_id=None):
    categories = db.query(Category).filter(
        Category.parent_id == parent_id,
        Category.is_active == True
    ).all()
    
    if not categories:
        return None
    
    keyboard = []
    for category in categories:
        # Subkategoriyalar mavjudligini tekshiramiz
        has_children = db.query(Category).filter(
            Category.parent_id == category.id,
            Category.is_active == True
        ).first() is not None
        
        button_text = f"📁 {category.name}" if has_children else f"📦 {category.name}"
        
        keyboard.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"admin_category_{category.id}"
        )])
    
    # Orqaga tugmasi
    if parent_id:
        parent_category = db.query(Category).filter(Category.id == parent_id).first()
        if parent_category and parent_category.parent_id:
            # Subkategoriyadan kategoriyaga qaytish
            keyboard.append([InlineKeyboardButton(
                text="◀️ Orqaga",
                callback_data=f"admin_category_{parent_category.parent_id}"
            )])
        else:
            # Asosiy kategoriyadan asosiy menyuga qaytish
            keyboard.append([InlineKeyboardButton(
                text="◀️ Asosiy menyu",
                callback_data="admin_back_to_main"
            )])
    else:
        # Asosiy menyudan admin menyusiga qaytish
        keyboard.append([InlineKeyboardButton(
            text="◀️ Admin menyusi",
            callback_data="admin_back_to_main"
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

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
            [InlineKeyboardButton(text="✏️ Boshqa rang", callback_data="color_custom")]
        ]
    )

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
    
    keyboard.append([InlineKeyboardButton(text="✏️ Boshqa razmer", callback_data="size_custom")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)