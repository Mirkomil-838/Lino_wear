from aiogram import Router, F
from aiogram.types import Message
from keyboards.main_menu import get_main_menu

router = Router()

@router.message()
async def unknown_command(message: Message):
    await message.answer(
        "❌ Noma'lum buyruq!\n"
        "Iltimos, quyidagi menyulardan foydalaning:",
        reply_markup=get_main_menu()
    )