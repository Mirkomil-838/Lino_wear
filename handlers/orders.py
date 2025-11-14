from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.db import get_db
from database.models import Order, User
from keyboards.main_menu import get_main_menu
from utils.states import UserStates
import json

router = Router()

@router.message(F.text == "📋 Buyurtmalarim")
async def show_my_orders(message: Message):
    db = next(get_db())
    
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if not user:
        await message.answer("Sizda hali buyurtmalar mavjud emas.")
        return
    
    orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
    
    if not orders:
        await message.answer("📭 Sizda hali buyurtmalar mavjud emas.")
        return
    
    for order in orders[:5]:  # Oxirgi 5 ta buyurtmani ko'rsatamiz
        order_text = (
            f"📦 Buyurtma #{order.id}\n"
            f"📅 Sana: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"💳 To'lov: {order.payment_type}\n"
            f"💰 Jami: {order.total_amount:,.0f} so'm\n"
            f"📊 Holati: {order.status}\n\n"
            f"📋 Mahsulotlar:\n"
        )
        
        # Buyurtmadagi mahsulotlarni ko'rsatamiz
        items = order.items
        for i, item in enumerate(items, 1):
            order_text += f"{i}. 🆔{item.get('product_id', 'N/A')} {item['product_name']}\n"
            order_text += f"   Rang: {item['color']}, Razmer: {item['size']}\n"
            order_text += f"   Miqdor: {item['quantity']} ta\n"
            order_text += f"   Narx: {item['price']:,.0f} so'm\n\n"
        
        await message.answer(order_text)
    
    if len(orders) > 5:
        await message.answer(f"📋 Jami {len(orders)} ta buyurtma. Faqat oxirgi 5 tasi ko'rsatilmoqda.")