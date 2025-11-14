import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database.db import init_db
from database.init_data import init_categories
from handlers.start import router as start_router
from handlers.categories import router as categories_router
from handlers.cart import router as cart_router
from handlers.admin import router as admin_router
from handlers.back_handler import router as back_router
from handlers.unknown import router as unknown_router

# Loggerni sozlash
logging.basicConfig(level=logging.INFO)

async def main():
    # Ma'lumotlar bazasini ishga tushirish
    init_db()
    
    # Boshlang'ich ma'lumotlarni qo'shish
    init_categories()
    
    # Bot va dispatcher yaratish
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Routerlarni qo'shish (tartib muhim)
    dp.include_router(start_router)
    dp.include_router(categories_router)
    dp.include_router(cart_router)
    dp.include_router(admin_router)
    dp.include_router(back_router)
    dp.include_router(unknown_router)  # Eng oxiriga
    
    # Botni ishga tushirish
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())