from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.db import get_db
from database.models import Category, Product, User, Order
from keyboards.admin import (
    get_admin_main_keyboard,
    get_categories_keyboard_admin,
    get_color_selection_keyboard,
    get_size_selection_keyboard
)
from keyboards.main_menu import get_main_menu
from utils.states import AdminStates
from config import ADMIN_IDS
import json

router = Router()

# Admin panelini ishga tushirish
@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Sizga ruxsat berilmagan!")
        return
    
    await message.answer(
        "👨‍💼 Admin paneliga xush kelibsiz!",
        reply_markup=get_admin_main_keyboard()
    )
    await state.set_state(AdminStates.main_menu)

# Asosiy admin menyusi
@router.message(AdminStates.main_menu, F.text == "📦 Mahsulot qo'shish")
async def start_adding_product(message: Message, state: FSMContext):
    await message.answer("Mahsulot nomini kiriting:")
    await state.set_state(AdminStates.adding_product_name)

@router.message(AdminStates.main_menu, F.text == "📊 Statistika")
async def show_statistics(message: Message):
    db = next(get_db())
    
    total_products = db.query(Product).count()
    total_orders = db.query(Order).count()
    total_users = db.query(User).count()
    pending_orders = db.query(Order).filter(Order.status == 'pending').count()
    
    await message.answer(
        f"📊 Bot statistikasi:\n\n"
        f"📦 Mahsulotlar: {total_products} ta\n"
        f"🛒 Jami buyurtmalar: {total_orders} ta\n"
        f"⏳ Kutayotgan buyurtmalar: {pending_orders} ta\n"
        f"👥 Foydalanuvchilar: {total_users} ta"
    )

@router.message(AdminStates.main_menu, F.text == "🏠 Asosiy menyu")
async def back_to_main_menu(message: Message, state: FSMContext):
    await message.answer(
        "Asosiy menyu:",
        reply_markup=get_main_menu()
    )
    await state.clear()

# Mahsulot qo'shish jarayoni - 1-qadam: Nomi
@router.message(AdminStates.adding_product_name)
async def process_product_name(message: Message, state: FSMContext):
    if len(message.text) < 2:
        await message.answer("Iltimos, mahsulot nomini to'liq kiriting (kamida 2 belgi):")
        return
    
    await state.update_data(product_name=message.text)
    await message.answer("Mahsulot tavsifini kiriting:")
    await state.set_state(AdminStates.adding_product_description)

# Mahsulot qo'shish jarayoni - 2-qadam: Tavsifi
@router.message(AdminStates.adding_product_description)
async def process_product_description(message: Message, state: FSMContext):
    if len(message.text) < 5:
        await message.answer("Iltimos, mahsulot tavsifini to'liq kiriting (kamida 5 belgi):")
        return
    
    await state.update_data(product_description=message.text)
    await message.answer("Mahsulot narxini kiriting (masalan: 25000):")
    await state.set_state(AdminStates.adding_product_price)

# Mahsulot qo'shish jarayoni - 3-qadam: Narxi
@router.message(AdminStates.adding_product_price)
async def process_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        if price <= 0:
            await message.answer("Iltimos, narxni musbat raqamda kiriting:")
            return
            
        await state.update_data(product_price=price)
        
        db = next(get_db())
        keyboard = get_categories_keyboard_admin(db)
        
        if keyboard:
            await message.answer(
                "Kategoriyani tanlang:\n\n"
                "📁 - Kategoriya (ichida boshqa kategoriyalar bor)\n"
                "📦 - Mahsulot qo'shish mumkin bo'lgan kategoriya",
                reply_markup=keyboard
            )
            await state.set_state(AdminStates.adding_product_category)
        else:
            await message.answer(
                "❌ Hozircha kategoriyalar mavjud emas. "
                "Iltimos, avval kategoriyalarni qo'shing.",
                reply_markup=get_admin_main_keyboard()
            )
            await state.set_state(AdminStates.main_menu)
    except ValueError:
        await message.answer("Iltimos, to'g'ri raqam kiriting (masalan: 25000):")

# Mahsulot qo'shish jarayoni - 4-qadam: Kategoriya tanlash
@router.callback_query(AdminStates.adding_product_category, F.data.startswith("admin_category_"))
async def process_product_category(callback: CallbackQuery, state: FSMContext):
    db = next(get_db())
    category_id = int(callback.data.split("_")[2])
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        await callback.answer("Kategoriya topilmadi!")
        return
    
    # Subkategoriyalarni tekshiramiz
    subcategories = db.query(Category).filter(
        Category.parent_id == category_id,
        Category.is_active == True
    ).all()
    
    if subcategories:
        # Subkategoriyalar mavjud, ularni ko'rsatamiz
        await callback.message.edit_text(
            f"📁 {category.name} kategoriyasi:\nQuyidagi bo'limlardan birini tanlang:",
            reply_markup=get_categories_keyboard_admin(db, category_id)
        )
    else:
        # Bu oxirgi kategoriya, mahsulot qo'shish uchun tanlandi
        await state.update_data(
            product_category_id=category_id, 
            product_category_name=category.name
        )
        await callback.message.answer("📸 Mahsulot rasmini yuboring:")
        await state.set_state(AdminStates.adding_product_image)

# Admin kategoriya menyusidan asosiy menyuga qaytish
@router.callback_query(AdminStates.adding_product_category, F.data == "admin_back_to_main")
async def admin_back_to_main(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "❌ Mahsulot qo'shish bekor qilindi.",
        reply_markup=get_admin_main_keyboard()
    )
    await state.set_state(AdminStates.main_menu)

# Mahsulot qo'shish jarayoni - 5-qadam: Rasm
@router.message(AdminStates.adding_product_image, F.photo)
async def process_product_image(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(product_image=photo_id)
    
    await message.answer(
        "🎨 Rangni tanlang:",
        reply_markup=get_color_selection_keyboard()
    )
    await state.set_state(AdminStates.adding_product_colors)

# Rang tanlash - asosiy ranglar
@router.callback_query(AdminStates.adding_product_colors, F.data.startswith("color_"))
async def process_product_colors(callback: CallbackQuery, state: FSMContext):
    color_data = callback.data
    
    if color_data == "color_custom":
        await callback.message.answer("✏️ Iltimos, rang nomini yozib yuboring (masalan: Binafsha):")
        await state.set_state(AdminStates.adding_custom_color)
        return
    
    color_name = color_data.split("_")[1]
    # Rang nomini o'zbekchaga o'giramiz
    color_translations = {
        'red': 'Qizil',
        'blue': "Ko'k", 
        'green': 'Yashil',
        'white': 'Oq',
        'black': 'Qora',
        'yellow': 'Sariq'
    }
    color_display = color_translations.get(color_name, color_name)
    
    await state.update_data(selected_colors=[color_display])
    
    await callback.message.answer(
        f"✅ Rang tanlandi: {color_display}\n\n"
        f"📏 Endi razmerni tanlang:",
        reply_markup=get_size_selection_keyboard()
    )
    await state.set_state(AdminStates.adding_product_sizes)

# Maxsus rang kiritish
@router.message(AdminStates.adding_custom_color)
async def process_custom_color(message: Message, state: FSMContext):
    if len(message.text) < 2:
        await message.answer("Iltimos, rang nomini to'liq kiriting:")
        return
        
    await state.update_data(selected_colors=[message.text])
    
    await message.answer(
        f"✅ Rang tanlandi: {message.text}\n\n"
        f"📏 Endi razmerni tanlang:",
        reply_markup=get_size_selection_keyboard()
    )
    await state.set_state(AdminStates.adding_product_sizes)

# Razmer tanlash - asosiy razmerlar
@router.callback_query(AdminStates.adding_product_sizes, F.data.startswith("size_"))
async def process_product_sizes(callback: CallbackQuery, state: FSMContext):
    size_data = callback.data
    
    if size_data == "size_custom":
        await callback.message.answer("✏️ Iltimos, razmerni yozib yuboring (masalan: 44 yoki L):")
        await state.set_state(AdminStates.adding_custom_size)
        return
    
    size_name = size_data.split("_")[1]
    await state.update_data(selected_sizes=[size_name])
    
    product_data = await state.get_data()
    await callback.message.answer(
        f"✅ Razmer tanlandi: {size_name}\n\n"
        f"Mahsulot muvaffaqiyatli qo'shildi!"
    )
    
    # Mahsulotni bazaga qo'shish (min_quantity siz)
    db = next(get_db())
    product = Product(
        name=product_data['product_name'],
        description=product_data['product_description'],
        price=product_data['product_price'],
        category_id=product_data['product_category_id'],
        image=product_data['product_image'],
        colors=product_data['selected_colors'],
        sizes=product_data['selected_sizes']
    )
    
    db.add(product)
    db.commit()
    
    category_name = product_data.get('product_category_name', 'Noma\'lum')
    colors_text = ", ".join(product_data['selected_colors'])
    sizes_text = ", ".join(product_data['selected_sizes'])
    
    await callback.message.answer_photo(
        photo=product_data['product_image'],
        caption=(
            f"✅ Mahsulot muvaffaqiyatli qo'shildi!\n\n"
            f"🆔 Mahsulot ID: {product.id}\n"
            f"📦 Nomi: {product_data['product_name']}\n"
            f"📝 Tavsifi: {product_data['product_description']}\n"
            f"📁 Kategoriya: {category_name}\n"
            f"💰 Narxi: {product_data['product_price']:,.0f} so'm\n"
            f"🎨 Ranglar: {colors_text}\n"
            f"📏 Razmerlar: {sizes_text}"
        ),
        reply_markup=get_admin_main_keyboard()
    )
    await state.set_state(AdminStates.main_menu)

# Maxsus razmer kiritish
@router.message(AdminStates.adding_custom_size)
async def process_custom_size(message: Message, state: FSMContext):
    if len(message.text) < 1:
        await message.answer("Iltimos, razmerni kiriting:")
        return
        
    await state.update_data(selected_sizes=[message.text])
    
    product_data = await state.get_data()
    
    # Mahsulotni bazaga qo'shish (min_quantity siz)
    db = next(get_db())
    product = Product(
        name=product_data['product_name'],
        description=product_data['product_description'],
        price=product_data['product_price'],
        category_id=product_data['product_category_id'],
        image=product_data['product_image'],
        colors=product_data['selected_colors'],
        sizes=product_data['selected_sizes']
    )
    
    db.add(product)
    db.commit()
    
    category_name = product_data.get('product_category_name', 'Noma\'lum')
    colors_text = ", ".join(product_data['selected_colors'])
    sizes_text = ", ".join(product_data['selected_sizes'])
    
    await message.answer_photo(
        photo=product_data['product_image'],
        caption=(
            f"✅ Mahsulot muvaffaqiyatli qo'shildi!\n\n"
            f"🆔 Mahsulot ID: {product.id}\n"
            f"📦 Nomi: {product_data['product_name']}\n"
            f"📝 Tavsifi: {product_data['product_description']}\n"
            f"📁 Kategoriya: {category_name}\n"
            f"💰 Narxi: {product_data['product_price']:,.0f} so'm\n"
            f"🎨 Ranglar: {colors_text}\n"
            f"📏 Razmerlar: {sizes_text}"
        ),
        reply_markup=get_admin_main_keyboard()
    )
    await state.set_state(AdminStates.main_menu)

# Noto'g'ri kiritilgan ma'lumotlar uchun handlerlar
@router.message(AdminStates.adding_product_name)
async def process_product_name_invalid(message: Message):
    await message.answer("Iltimos, mahsulot nomini matn shaklida kiriting:")

@router.message(AdminStates.adding_product_description)
async def process_description_invalid(message: Message):
    await message.answer("Iltimos, mahsulot tavsifini matn shaklida kiriting:")

@router.message(AdminStates.adding_product_price)
async def process_price_invalid(message: Message):
    await message.answer("Iltimos, mahsulot narxini raqam shaklida kiriting (masalan: 25000):")

@router.message(AdminStates.adding_product_image)
async def process_image_invalid(message: Message):
    await message.answer("Iltimos, mahsulot rasmini yuboring (faqat rasm qabul qilinadi):")

@router.message(AdminStates.adding_custom_color)
async def process_custom_color_invalid(message: Message):
    await message.answer("Iltimos, rang nomini matn shaklida kiriting:")

@router.message(AdminStates.adding_custom_size)
async def process_custom_size_invalid(message: Message):
    await message.answer("Iltimos, razmerni kiriting:")

# Admin paneliga boshqa xabarlar
@router.message(AdminStates.main_menu)
async def process_admin_unknown(message: Message):
    await message.answer(
        "Iltimos, quyidagi tugmalardan foydalaning:",
        reply_markup=get_admin_main_keyboard()
    )
    
