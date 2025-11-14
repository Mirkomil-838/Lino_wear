import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', '@your_channel')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///shop.db')

# To'lov turlari
PAYMENT_TYPES = ['Naqd', 'Click', 'Payme', 'Bank kartasi']