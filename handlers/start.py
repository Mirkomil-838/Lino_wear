from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from database.db import get_db
from database.models import User
from keyboards.main_menu import get_main_menu
from utils.states import UserStates

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    db = next(get_db())
    
    # Foydalanuvchini bazaga qo'shish
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if not user:
        user = User(
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name
        )
        db.add(user)
        db.commit()
    
    # Obuna tekshiruvsiz to'g'ridan-to'g'ri asosiy menyuni ko'rsatamiz
    await message.answer(
        f"Assalomu alaykum {message.from_user.full_name}! 🛍️\n"
        f"Online do'konimizga xush kelibsiz!",
        reply_markup=get_main_menu()
    )
    await state.set_state(UserStates.main_menu)

@router.message(F.text == "ℹ️ Ma'lumot")
async def show_info(message: Message):
    await message.answer(
        "🛍️ Online Do'kon Boti\n\n"
        "Bizning bot orqali siz:\n"
        "• Turli kategoriyalardagi mahsulotlarni ko'rishingiz mumkin\n"
        "• Mahsulotlarni savatga qo'shishingiz mumkin\n"
        "• Buyurtma berishingiz mumkin\n\n"
        "Bot sodd va qulay interfeysga ega!"
    )

@router.message(F.text == "📞 Aloqa")
async def show_contact(message: Message):
    await message.answer(
        "📞 Bog'lanish uchun:\n\n"
        "Telefon: +998901234567\n"
        "Email: info@example.com\n"
        "Manzil: Toshkent shahri\n\n"
        "Ish vaqti: 09:00 - 18:00"
    )
    
from aiogram.types import WebAppInfo

# Start handlerda web app tugmasini qo'shing
