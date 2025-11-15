import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

# ADMIN_IDS ni xavfsiz o'qish va tekshirish
ADMIN_IDS_STR = os.getenv('ADMIN_IDS', '')
ADMIN_IDS = []
if ADMIN_IDS_STR.strip():
    try:
        ADMIN_IDS = [int(admin_id.strip()) for admin_id in ADMIN_IDS_STR.split(',')]
        print(f"✅ Admin ID lar yuklandi: {ADMIN_IDS}")
    except ValueError as e:
        print(f"❌ Admin ID larni o'qishda xatolik: {e}")
        ADMIN_IDS = []

# Agar admin ID lar bo'sh bo'lsa, console ga xabar beramiz
if not ADMIN_IDS:
    print("⚠️ Diqqat: ADMIN_IDS bo'sh. Iltimos, .env faylida ADMIN_IDS ni ko'rsating.")

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///shop.db')

# To'lov turlari
PAYMENT_TYPES = ['Naqd', 'Click', 'Payme', 'Bank kartasi']

# Yetkazib berish narxi
DELIVERY_PRICE = 15000  # 15,000 so'm