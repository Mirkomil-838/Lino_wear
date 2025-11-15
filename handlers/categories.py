from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.db import get_db
from database.models import Category, Product, CartItem, User
from keyboards.categories import (
    get_main_categories_keyboard,
    get_subcategories_keyboard, 
    get_products_keyboard,
    get_color_selection_keyboard,
    get_size_selection_keyboard
)
from keyboards.cart import get_cart_keyboard
from keyboards.main_menu import get_main_menu
from utils.states import UserStates

router = Router()

# Kategoriya bo'limini ochish
@router.message(F.text == "🛍 Kategoriya")
async def show_main_categories(message: Message, state: FSMContext):
    db = next(get_db())
    
    await message.answer(
        "🏪 Do'konimizdagi asosiy kategoriyalar:\n\n"
        "Quyidagi kategoriyalardan birini tanlang:",
        reply_markup=get_main_categories_keyboard(db)
    )
    await state.set_state(UserStates.choosing_main_category)

# Asosiy kategoriya tanlash (Reply)
@router.message(UserStates.choosing_main_category)
async def process_main_category(message: Message, state: FSMContext):
    db = next(get_db())
    
    # Orqaga tekshiruvi
    if message.text == "🏠 Asosiy menyu":
        await message.answer("Asosiy menyu:", reply_markup=get_main_menu())
        await state.set_state(UserStates.main_menu)
        return
    
    # Kategoriyani topish
    category = db.query(Category).filter(
        Category.name == message.text,
        Category.parent_id == None
    ).first()
    
    if not category:
        await message.answer("Kategoriya topilmadi! Iltimos, tugmalardan foydalaning.")
        return
    
    # Subkategoriyalarni ko'rsatish
    subcategories = db.query(Category).filter(
        Category.parent_id == category.id,
        Category.is_active == True
    ).all()
    
    if not subcategories:
        # Agar subkategoriya yo'q bo'lsa, to'g'ridan-to'g'ri mahsulotlarni ko'rsatamiz
        products = db.query(Product).filter(
            Product.category_id == category.id,
            Product.is_active == True
        ).all()
        
        if products:
            # Har bir mahsulotni alohida rasm va ma'lumotlari bilan chiqaramiz
            for product in products:
                await send_product_with_image(message, product, category.id)
            
            products_count = len(products)
            await message.answer(
                f"📊 {category.name} kategoriyasida jami {products_count} ta mahsulot mavjud.",
                reply_markup=get_main_categories_keyboard(db)
            )
            await state.set_state(UserStates.choosing_main_category)
        else:
            await message.answer(
                f"❌ {category.name} kategoriyasida hali mahsulotlar mavjud emas!",
                reply_markup=get_main_categories_keyboard(db)
            )
        return
    
    # Subkategoriyalar mavjud bo'lsa
    await state.update_data(main_category_id=category.id, main_category_name=category.name)
    
    await message.answer(
        f"📁 {category.name} kategoriyasi:\n\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=get_subcategories_keyboard(db, category.id)
    )
    await state.set_state(UserStates.choosing_subcategory)

# Subkategoriya tanlash (Reply) - MAHSULOTLARNI RASMI BILAN KO'RSATISH
@router.message(UserStates.choosing_subcategory)
async def process_subcategory(message: Message, state: FSMContext):
    db = next(get_db())
    user_data = await state.get_data()
    main_category_id = user_data.get('main_category_id')
    
    # Orqaga tekshiruvi
    if message.text == "◀️ Orqaga":
        await show_main_categories(message, state)
        return
    
    if message.text == "🏠 Asosiy menyu":
        await message.answer("Asosiy menyu:", reply_markup=get_main_menu())
        await state.set_state(UserStates.main_menu)
        return
    
    # Subkategoriyani topish
    subcategory = db.query(Category).filter(
        Category.name == message.text,
        Category.parent_id == main_category_id
    ).first()
    
    if not subcategory:
        await message.answer("Bo'lim topilmadi! Iltimos, tugmalardan foydalaning.")
        return
    
    # Subkategoriyadagi mahsulotlarni olish
    products = db.query(Product).filter(
        Product.category_id == subcategory.id,
        Product.is_active == True
    ).all()
    
    if not products:
        await message.answer(
            f"❌ {message.text} bo'limida hali mahsulotlar mavjud emas!",
            reply_markup=get_subcategories_keyboard(db, main_category_id)
        )
        return
    
    # Har bir mahsulotni alohida rasm va ma'lumotlari bilan chiqaramiz
    for product in products:
        await send_product_with_image(message, product, subcategory.id)
    
    # Mahsulotlar soni haqida xabar
    products_count = len(products)
    await message.answer(
        f"📊 {message.text} bo'limida jami {products_count} ta mahsulot mavjud.",
        reply_markup=get_subcategories_keyboard(db, main_category_id)
    )
    
    await state.update_data(subcategory_id=subcategory.id, subcategory_name=message.text)

# Mahsulotni rasm va ma'lumotlari bilan yuborish funksiyasi
async def send_product_with_image(message, product, category_id):
    """Mahsulotni rasm va batafsil ma'lumotlari bilan yuboradi"""
    
    # Mahsulot ma'lumotlarini tayyorlash
    product_text = (
        f"🆔 Mahsulot ID: {product.id}\n"
        f"📦 {product.name}\n"
        f"💰 Narxi: {product.price:,.0f} so'm\n"
        f"📝 {product.description or 'Tavsif mavjud emas'}\n\n"
    )
    
    # Ranglar va razmerlarni ko'rsatish
    if product.colors:
        colors_text = ", ".join(product.colors)
        product_text += f"🎨 Ranglar: {colors_text}\n"
    
    if product.sizes:
        sizes_text = ", ".join(product.sizes)
        product_text += f"📏 Razmerlar: {sizes_text}\n"
    
    product_text += f"\n🛒 Mahsulotni tanlang:"
    
    # Mahsulot tanlash uchun keyboard
    keyboard = get_products_keyboard([product], category_id)
    
    # Agar mahsulot rasmi bo'lsa, rasm bilan chiqaramiz
    if product.image:
        try:
            await message.answer_photo(
                photo=product.image,
                caption=product_text,
                reply_markup=keyboard
            )
        except Exception as e:
            # Agar rasm bilan muammo bo'lsa, oddiy xabar
            await message.answer(
                f"🖼️ {product_text}",
                reply_markup=keyboard
            )
    else:
        # Agar rasm bo'lmasa, oddiy xabar
        await message.answer(
            product_text,
            reply_markup=keyboard
        )

# Mahsulot tanlash (Inline)
@router.callback_query(F.data.startswith("product_"))
async def process_product(callback: CallbackQuery, state: FSMContext):
    db = next(get_db())
    product_id = int(callback.data.split("_")[1])
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        await callback.answer("Mahsulot topilmadi!")
        return
    
    # Mahsulot ma'lumotlarini saqlash
    await state.update_data(
        selected_product_id=product_id,
        selected_product_name=product.name,
        selected_product_price=product.price,
        selected_product_description=product.description,
        selected_product_image=product.image
    )
    
    # Ranglar va razmerlarni formatlab ko'rsatamiz
    colors_text = "\n".join([f"• {color}" for color in (product.colors or [])]) 
    sizes_text = ", ".join(product.sizes or [])
    
    # Mahsulot ma'lumotlarini chiroyli ko'rsatamiz
    product_text = (
        f"🆔 Mahsulot ID: {product.id}\n"
        f"🛍 {product.name}\n\n"
        f"📝 {product.description or 'Tavsif mavjud emas'}\n\n"
        f"💰 Narxi: {product.price:,.0f} so'm\n"
    )
    
    if colors_text:
        product_text += f"🎨 Mavjud ranglar:\n{colors_text}\n\n"
    
    if sizes_text:
        product_text += f"📏 Mavjud razmerlar: {sizes_text}\n\n"
    
    product_text += "Iltimos, rangni tanlang:"
    
    # Agar mahsulot rasmi bo'lsa, rasm bilan birga yuboramiz
    if product.image:
        try:
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=product.image,
                caption=product_text,
                reply_markup=get_color_selection_keyboard()
            )
        except:
            await callback.message.edit_text(
                product_text,
                reply_markup=get_color_selection_keyboard()
            )
    else:
        await callback.message.edit_text(
            product_text,
            reply_markup=get_color_selection_keyboard()
        )
    
    await state.set_state(UserStates.choosing_color)

# ... (qolgan handlerlar o'zgarmaydi - rang tanlash, razmer tanlash, miqdor kiritish)

# Rang tanlash (Inline)
@router.callback_query(UserStates.choosing_color, F.data.startswith("color_"))
async def process_color(callback: CallbackQuery, state: FSMContext):
    color_data = callback.data
    
    if color_data == "color_custom":
        await callback.message.answer("✏️ Iltimos, rang nomini yozib yuboring (masalan: Binafsha):")
        await state.set_state(UserStates.choosing_custom_color)
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
    
    await state.update_data(selected_color=color_display)
    
    await callback.message.answer(
        f"✅ Rang tanlandi: {color_display}\n\n"
        f"📏 Endi razmerni tanlang:",
        reply_markup=get_size_selection_keyboard()
    )
    await state.set_state(UserStates.choosing_size)

# Maxsus rang kiritish
@router.message(UserStates.choosing_custom_color)
async def process_custom_color(message: Message, state: FSMContext):
    if len(message.text) < 2:
        await message.answer("Iltimos, rang nomini to'liq kiriting:")
        return
        
    await state.update_data(selected_color=message.text)
    
    await message.answer(
        f"✅ Rang tanlandi: {message.text}\n\n"
        f"📏 Endi razmerni tanlang:",
        reply_markup=get_size_selection_keyboard()
    )
    await state.set_state(UserStates.choosing_size)

# Razmer tanlash (Inline)
@router.callback_query(UserStates.choosing_size, F.data.startswith("size_"))
async def process_size(callback: CallbackQuery, state: FSMContext):
    size_data = callback.data
    
    if size_data == "size_custom":
        await callback.message.answer("✏️ Iltimos, razmerni yozib yuboring (masalan: 44 yoki L):")
        await state.set_state(UserStates.choosing_custom_size)
        return
    
    size_name = size_data.split("_")[1]
    await state.update_data(selected_size=size_name)
    
    await callback.message.answer(
        f"✅ Razmer tanlandi: {size_name}\n\n"
        f"📦 Miqdorni kiriting:"
    )
    await state.set_state(UserStates.entering_quantity)

# Maxsus razmer kiritish
@router.message(UserStates.choosing_custom_size)
async def process_custom_size(message: Message, state: FSMContext):
    if len(message.text) < 1:
        await message.answer("Iltimos, razmerni kiriting:")
        return
        
    await state.update_data(selected_size=message.text)
    
    await message.answer(
        f"✅ Razmer tanlandi: {message.text}\n\n"
        f"📦 Miqdorni kiriting:"
    )
    await state.set_state(UserStates.entering_quantity)

# Miqdor kiritish
@router.message(UserStates.entering_quantity)
async def process_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
        
        if quantity <= 0:
            await message.answer("❌ Iltimos, 0 dan katta miqdor kiriting!")
            return
        
        # Savatga qo'shish
        db = next(get_db())
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                full_name=message.from_user.full_name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        product_data = await state.get_data()
        
        cart_item = CartItem(
            user_id=user.id,
            product_id=product_data['selected_product_id'],
            color=product_data['selected_color'],
            size=product_data['selected_size'],
            quantity=quantity
        )
        
        db.add(cart_item)
        db.commit()
        
        # Savatdagi jami mahsulotlar sonini hisoblaymiz
        total_cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).count()
        
        success_text = (
            f"✅ Mahsulot savatga qo'shildi!\n\n"
            f"🆔 Mahsulot ID: {product_data['selected_product_id']}\n"
            f"📦 {product_data['selected_product_name']}\n"
            f"🎨 Rang: {product_data['selected_color']}\n"
            f"📏 Razmer: {product_data['selected_size']}\n"
            f"🔢 Miqdor: {quantity} ta\n"
            f"💰 Jami: {product_data['selected_product_price'] * quantity:,.0f} so'm\n\n"
            f"🛒 Savatingizda jami {total_cart_items} ta mahsulot bor"
        )
        
        await message.answer(
            success_text,
            reply_markup=get_cart_keyboard([cart_item])
        )
        await state.set_state(UserStates.cart)
        
    except ValueError:
        await message.answer("❌ Iltimos, to'g'ri raqam kiriting!")

# Orqaga qaytish (mahsulotlar ro'yxatidan subkategoriyaga)
@router.callback_query(F.data.startswith("back_category_"))
async def back_to_subcategory(callback: CallbackQuery, state: FSMContext):
    db = next(get_db())
    category_id = int(callback.data.split("_")[2])
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if category:
        # Kategoriyaning ota kategoriyasini topamiz
        parent_category = db.query(Category).filter(Category.id == category.parent_id).first()
        
        if parent_category:
            # Subkategoriyalarga qaytamiz
            await callback.message.answer(
                f"📁 {parent_category.name} kategoriyasi:\n\n"
                "Quyidagi bo'limlardan birini tanlang:",
                reply_markup=get_subcategories_keyboard(db, parent_category.id)
            )
            await state.set_state(UserStates.choosing_subcategory)
            await state.update_data(main_category_id=parent_category.id)

# Asosiy menyuga qaytish
@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🏠 Asosiy menyu:",
        reply_markup=get_main_menu()
    )
    await state.set_state(UserStates.main_menu)

# Noto'g'ri harakatlar uchun handlerlar
@router.message(UserStates.choosing_main_category)
async def handle_main_category_invalid(message: Message):
    await message.answer("Iltimos, kategoriyani tugma orqali tanlang.")

@router.message(UserStates.choosing_subcategory)
async def handle_subcategory_invalid(message: Message):
    await message.answer("Iltimos, bo'limni tugma orqali tanlang.")

@router.message(UserStates.entering_quantity)
async def handle_quantity_invalid(message: Message):
    await message.answer("❌ Iltimos, miqdorni raqamda kiriting:")

# Savatga o'tish
@router.message(F.text == "🛒 Savat")
async def handle_cart_button(message: Message, state: FSMContext):
    from handlers.cart import show_cart
    await show_cart(message, state)