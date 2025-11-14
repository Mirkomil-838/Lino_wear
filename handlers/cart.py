from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.db import get_db
from database.models import CartItem, User, Product, Order
from keyboards.cart import (
    get_cart_keyboard, 
    get_phone_keyboard, 
    get_location_keyboard,
    get_payment_types_keyboard
)
from keyboards.main_menu import get_main_menu
from utils.states import UserStates
from config import PAYMENT_TYPES, ADMIN_IDS

router = Router()

@router.message(F.text == "🛒 Savat")
async def show_cart(message: Message, state: FSMContext):
    db = next(get_db())
    
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    
    if not cart_items:
        await message.answer("Savatda mahsulotlar mavjud emas!", reply_markup=get_main_menu())
        return
    
    total = 0
    cart_text = "🛒 Sizning savatingiz:\n\n"
    
    for item in cart_items:
        item_total = item.product.price * item.quantity
        total += item_total
        cart_text += f"🆔 Mahsulot ID: {item.product.id}\n"
        cart_text += f"📦 {item.product.name}\n"
        cart_text += f"   Rang: {item.color}, Razmer: {item.size}\n"
        cart_text += f"   Miqdor: {item.quantity} ta\n"
        cart_text += f"   Narx: {item_total:,.0f} so'm\n\n"
    
    cart_text += f"💰 Jami: {total:,.0f} so'm"
    
    await message.answer(cart_text, reply_markup=get_cart_keyboard(cart_items))
    await state.set_state(UserStates.cart)

@router.callback_query(F.data.startswith("remove_"))
async def remove_from_cart(callback: CallbackQuery, state: FSMContext):
    db = next(get_db())
    item_id = int(callback.data.split("_")[1])
    
    cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if cart_item:
        db.delete(cart_item)
        db.commit()
        await callback.answer("Mahsulot savatdan olib tashlandi!")
        await show_cart(callback.message, state)
    else:
        await callback.answer("Mahsulot topilmadi!")

@router.callback_query(F.data == "place_order")
async def start_ordering(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Iltimos, telefon raqamingizni yuboring:",
        reply_markup=get_phone_keyboard()
    )
    await state.set_state(UserStates.ordering_phone)

@router.message(UserStates.ordering_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    
    await message.answer(
        "Endi lokatsiyangizni yuboring:",
        reply_markup=get_location_keyboard()
    )
    await state.set_state(UserStates.ordering_location)

@router.message(UserStates.ordering_location, F.location)
async def process_location(message: Message, state: FSMContext):
    location = f"Lat: {message.location.latitude}, Lon: {message.location.longitude}"
    await state.update_data(location=location)
    
    await message.answer(
        "To'lov turini tanlang:",
        reply_markup=get_payment_types_keyboard()
    )
    await state.set_state(UserStates.ordering_payment)

@router.message(UserStates.ordering_payment, F.text.in_(PAYMENT_TYPES))
async def process_payment(message: Message, state: FSMContext, bot: Bot):
    db = next(get_db())
    user_data = await state.get_data()
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    # Savatdagi mahsulotlarni olish
    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    
    if not cart_items:
        await message.answer("Savatda mahsulotlar mavjud emas!")
        return
    
    # Buyurtma yaratish
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    
    order_items = []
    for item in cart_items:
        order_items.append({
            'product_id': item.product.id,  # ✅ Mahsulot ID qo'shildi
            'product_name': item.product.name,
            'color': item.color,
            'size': item.size,
            'quantity': item.quantity,
            'price': item.product.price
        })
    
    order = Order(
        user_id=user.id,
        items=order_items,
        total_amount=total_amount,
        phone=user_data['phone'],
        location=user_data['location'],
        payment_type=message.text
    )
    
    db.add(order)
    
    # Savatni tozalash
    db.query(CartItem).filter(CartItem.user_id == user.id).delete()
    db.commit()
    
    # Adminlarga xabar yuborish (MAHSULOT ID BILAN)
    order_text = "🛒 YANGI BUYURTMA!\n\n"
    order_text += f"👤 Mijoz: {user.full_name}\n"
    order_text += f"📞 Telefon: {user_data['phone']}\n"
    order_text += f"📍 Manzil: {user_data['location']}\n"
    order_text += f"💳 To'lov turi: {message.text}\n\n"
    order_text += "📦 Mahsulotlar:\n"
    
    for item in order_items:
        order_text += f"🆔 Mahsulot ID: {item['product_id']}\n"
        order_text += f"📦 Nomi: {item['product_name']}\n"
        order_text += f"   Rang: {item['color']}, Razmer: {item['size']}\n"
        order_text += f"   Miqdor: {item['quantity']} ta\n"
        order_text += f"   Narx: {item['price']:,.0f} so'm\n\n"
    
    order_text += f"💰 Jami: {total_amount:,.0f} so'm"
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, order_text)
        except Exception as e:
            print(f"Adminga xabar yuborishda xatolik: {e}")
    
    await message.answer(
        "✅ Buyurtmangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.",
        reply_markup=get_main_menu()
    )
    await state.set_state(UserStates.main_menu)

@router.message(UserStates.ordering_payment, F.text == "◀️ Ortga")
async def back_to_location(message: Message, state: FSMContext):
    await message.answer(
        "Lokatsiyangizni yuboring:",
        reply_markup=get_location_keyboard()
    )
    await state.set_state(UserStates.ordering_location)
    
@router.callback_query(F.data == "main_menu")
async def back_to_main_menu_from_cart(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=get_main_menu()
    )
    await state.set_state(UserStates.main_menu)
    
@router.message(UserStates.ordering_phone)
async def process_phone_invalid(message: Message):
    await message.answer("Iltimos, telefon raqamingizni tugma orqali yuboring:", reply_markup=get_phone_keyboard())

@router.message(UserStates.ordering_location)
async def process_location_invalid(message: Message):
    await message.answer("Iltimos, lokatsiyangizni tugma orqali yuboring:", reply_markup=get_location_keyboard())

@router.message(UserStates.ordering_payment)
async def process_payment_invalid(message: Message):
    await message.answer("Iltimos, to'lov turini tanlang:", reply_markup=get_payment_types_keyboard())

@router.message(UserStates.cart)
async def process_cart_actions(message: Message):
    if message.text == "🛒 Savat":
        await show_cart(message, state=None)
    else:
        await message.answer("Savat menyusidan foydalaning yoki asosiy menyuga qayting.", reply_markup=get_main_menu())