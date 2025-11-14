from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.models import Category, Product
from sqlalchemy.orm import Session

def get_categories_keyboard(db: Session, parent_id=None):
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

def get_products_keyboard(products, category_id):
    keyboard = []
    
    for product in products:
        # Mahsulot nomini qisqartirib ko'rsatamiz
        product_name = product.name
        if len(product_name) > 15:
            product_name = product_name[:15] + "..."
        
        # Narxni formatlab ko'rsatamiz
        price_formatted = f"{product.price:,.0f}".replace(",", " ")
        
        button_text = f"🆔{product.id} {product_name} - {price_formatted} so'm"
        
        keyboard.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"product_{product.id}"
        )])
    
    # Orqaga qaytish tugmasi
    keyboard.append([InlineKeyboardButton(
            text="◀️ Asosiy menyu",
            callback_data="back_to_main"
        )])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)