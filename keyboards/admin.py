from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database.models import Category, Product
from sqlalchemy.orm import Session

def get_admin_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📦 Mahsulot qo'shish"), 
                KeyboardButton(text="🗑️ Mahsulotlarni boshqarish")
            ],
            [
                KeyboardButton(text="📢 Xabar yuborish"),
                KeyboardButton(text="📊 Statistika")
            ],
            [
                KeyboardButton(text="🏠 Asosiy menyu")
            ]
        ],
        resize_keyboard=True
    )

# ✅ Yangi: Mahsulotlarni boshqarish keyboardi
def get_products_management_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 Mahsulotlar ro'yxati"),
                KeyboardButton(text="❌ Mahsulot o'chirish")
            ],
            [
                KeyboardButton(text="◀️ Orqaga")
            ]
        ],
        resize_keyboard=True
    )

# ✅ Yangi: Mahsulotlar ro'yxati keyboardi
def get_products_list_keyboard(products, page=0, products_per_page=10):
    keyboard = []
    
    # Mahsulotlarni sahifalab ko'rsatamiz
    start_idx = page * products_per_page
    end_idx = start_idx + products_per_page
    current_products = products[start_idx:end_idx]
    
    for product in current_products:
        product_name = product.name
        if len(product_name) > 20:
            product_name = product_name[:20] + "..."
        
        button_text = f"🆔{product.id} {product_name} - {product.price:,.0f} so'm"
        keyboard.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"view_product_{product.id}"
        )])
    
    # Sahifa navigatsiyasi
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton(
            text="◀️ Oldingi",
            callback_data=f"products_page_{page-1}"
        ))
    
    if end_idx < len(products):
        navigation_buttons.append(InlineKeyboardButton(
            text="Keyingi ▶️",
            callback_data=f"products_page_{page+1}"
        ))
    
    if navigation_buttons:
        keyboard.append(navigation_buttons)
    
    # Orqaga tugmasi
    keyboard.append([InlineKeyboardButton(
        text="◀️ Orqaga",
        callback_data="back_to_management"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ✅ Yangi: Mahsulotni o'chirish tasdiqlash keyboardi
def get_product_delete_confirmation_keyboard(product_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ HA, O'chirish", callback_data=f"confirm_delete_{product_id}"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_delete")
            ]
        ]
    )

# ✅ Yangi: Mahsulot ma'lumotlari keyboardi
def get_product_details_keyboard(product_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ O'chirish", callback_data=f"delete_product_{product_id}"),
                InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_products_list")
            ]
        ]
    )

# Xabar yuborish tasdiqlash keyboardi
def get_broadcast_confirmation_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Xabarni yuborish", callback_data="confirm_broadcast"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_broadcast")
            ]
        ]
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
            # Asosiy kategoriyadan admin menyusiga qaytish
            keyboard.append([InlineKeyboardButton(
                text="◀️ Admin menyusi",
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
            [
                InlineKeyboardButton(text="✏️ Boshqa rang", callback_data="color_custom"),
                InlineKeyboardButton(text="◀️ Orqaga", callback_data="cancel_selection")
            ]
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
    
    keyboard.append([
        InlineKeyboardButton(text="✏️ Boshqa razmer", callback_data="size_custom"),
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="cancel_selection")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)