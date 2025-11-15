from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.main_menu import get_main_menu
from utils.states import UserStates

router = Router()

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    # ✅ TUZATILGAN: Yangi xabar yuboramiz (edit_text o'rniga)
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=get_main_menu()
    )
    await state.set_state(UserStates.main_menu)