from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from database.db import get_db
from database.models import User
from keyboards.main_menu import get_main_menu, get_subscription_check_keyboard
from keyboards.categories import get_categories_keyboard
from utils.states import UserStates
from config import CHANNEL_USERNAME
from aiogram import Bot

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
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
    
    # Obunani tekshirish
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
        if member.status in ['member', 'administrator', 'creator']:
            await message.answer(
                f"Assalomu alaykum {message.from_user.full_name}! 🛍️\n"
                f"Online do'konimizga xush kelibsiz!",
                reply_markup=get_main_menu()
            )
            await state.set_state(UserStates.main_menu)
        else:
            await message.answer(
                "Botdan foydalanish uchun avval kanalimizga obuna bo'ling:",
                reply_markup=get_subscription_check_keyboard()
            )
            await state.set_state(UserStates.waiting_for_subscription)
    except Exception as e:
        await message.answer(
            "Botdan foydalanish uchun avval kanalimizga obuna bo'ling:",
            reply_markup=get_subscription_check_keyboard()
        )
        await state.set_state(UserStates.waiting_for_subscription)

@router.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, callback.from_user.id)
        if member.status in ['member', 'administrator', 'creator']:
            # Yangi xabar yuboramiz
            await callback.message.answer(
                f"Assalomu alaykum {callback.from_user.full_name}! 🛍️\n"
                f"Online do'konimizga xush kelibsiz!",
                reply_markup=get_main_menu()
            )
            await state.set_state(UserStates.main_menu)
        else:
            await callback.answer("Siz hali kanalga obuna bo'lmagansiz!", show_alert=True)
    except Exception as e:
        await callback.answer("Xatolik yuz berdi! Iltimos qayta urinib ko'ring.", show_alert=True)
        
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
