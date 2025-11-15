from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.db import get_db
from database.models import Category, Product, CartItem, User
from keyboards.categories import get_categories_keyboard, get_products_keyboard
from keyboards.cart import get_cart_keyboard
from keyboards.admin import get_color_selection_keyboard, get_size_selection_keyboard
from keyboards.main_menu import get_main_menu
from utils.states import UserStates
from sqlalchemy.orm import Session

router = Router()

# Optom bo'limini ochish
@router.message(F.text == "🛍 Optom")
async def show_categories(message: Message, state: FSMContext):
    db = next(get_db())
    await message.answer(
        "🏪 Do'konimizdagi kategoriyalar:\n\n"
        "Quyidagi kategoriyalardan birini tanlang:",
        reply_markup=get_categories_keyboard(db)
    )
    await state.set_state(UserStates.choosing_category)

# Kategoriya tanlash
@router.callback_query(F.data.startswith("category_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    db = next(get_db())
    category_id = int(callback.data.split("_")[1])
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        await callback.answer("Kategoriya topilmadi!")
        return
    
    # Subkategoriyalarni tekshirish
    subcategories = db.query(Category).filter(
        Category.parent_id == category_id,
        Category.is_active == True
    ).all()
    
    if subcategories:
        # Subkategoriyalar mavjud
        subcat_names = [sub.name for sub in subcategories]
        subcats_text = "\n".join([f"• {name}" for name in subcat_names])
        
        await callback.message.edit_text(
            f"📁 {category.name} kategoriyasi:\n\n"
            f"Quyidagi bo'limlardan birini tanlang:\n{subcats_text}",
            reply_markup=get_categories_keyboard(db, category_id)
        )
    else:
        # Mahsulotlarni ko'rsatish
        products = db.query(Product).filter(
            Product.category_id == category_id,
            Product.is_active == True
        ).all()
        
        if products:
            products_count = len(products)
            await callback.message.edit_text(
                f"📦 {category.name} kategoriyasidagi mahsulotlar "
                f"({products_count} ta):",
                reply_markup=get_products_keyboard(products, category_id)
            )
            await state.set_state(UserStates.viewing_products)
        else:
            await callback.answer(
                f"❌ {category.name} kategoriyasida hali mahsulotlar mavjud emas!", 
                show_alert=True
            )

# Mahsulot tanlash
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
    
    # Mahsulot ma'lumotlarini chiroyli ko'rsatamiz (ID bilan)
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
            # Agar rasm bilan muammo bo'lsa, oddiy xabar yuboramiz
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

# Rang tanlash
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

# Razmer tanlash
@router.callback_query(UserStates.choosing_size, F.data.startswith("size_"))
async def process_size(callback: CallbackQuery, state: FSMContext):
    size_data = callback.data
    
    if size_data == "size_custom":
        await callback.message.answer("✏️ Iltimos, razmerni yozib yuboring (masalan: 44 yoki L):")
        await state.set_state(UserStates.choosing_custom_size)
        return
    
    size_name = size_data.split("_")[1]
    await state.update_data(selected_size=size_name)
    
    product_data = await state.get_data()
    
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
            # Agar foydalanuvchi bazada yo'q bo'lsa, yangi qo'shamiz
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

# Asosiy menyuga qaytish
@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    # ✅ TUZATILGAN: Yangi xabar yuboramiz
    await callback.message.answer(
        "🏠 Asosiy menyu:",
        reply_markup=get_main_menu()
    )
    await state.set_state(UserStates.main_menu)

# Orqaga qaytish (kategoriya ichida)
@router.callback_query(F.data.startswith("back_category_"))
async def back_to_category(callback: CallbackQuery, state: FSMContext):
    db = next(get_db())
    category_id = int(callback.data.split("_")[2])
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if category:
        products = db.query(Product).filter(
            Product.category_id == category_id,
            Product.is_active == True
        ).all()
        
        if products:
            products_count = len(products)
            await callback.message.edit_text(
                f"📦 {category.name} kategoriyasidagi mahsulotlar "
                f"({products_count} ta):",
                reply_markup=get_products_keyboard(products, category_id)
            )
            await state.set_state(UserStates.viewing_products)

# Noto'g'ri harakatlar uchun handlerlar
@router.message(UserStates.choosing_category)
async def handle_category_invalid(message: Message):
    await message.answer("Iltimos, kategoriyani tugma orqali tanlang.")

@router.message(UserStates.viewing_products)
async def handle_products_invalid(message: Message):
    await message.answer("Iltimos, mahsulotni tugma orqali tanlang.")

@router.message(UserStates.entering_quantity)
async def handle_quantity_invalid(message: Message, state: FSMContext):
    await message.answer("❌ Iltimos, miqdorni raqamda kiriting:")

@router.message(UserStates.choosing_color)
async def handle_color_invalid(message: Message):
    await message.answer("Iltimos, rangni tugma orqali tanlang.")

@router.message(UserStates.choosing_size)
async def handle_size_invalid(message: Message):
    await message.answer("Iltimos, razmerni tugma orqali tanlang.")

# Kategoriya va mahsulotlar bo'limida noto'g'ri xabarlar
@router.message(F.text.in_(["🛍 Kategoriya", "🛒 Savat"]))
async def handle_main_menu_buttons(message: Message, state: FSMContext):
    if message.text == "🛍 Kategoriya":
        db = next(get_db())
        await message.answer(
            "🏪 Do'konimizdagi kategoriyalar:\n\n"
            "Quyidagi kategoriyalardan birini tanlang:",
            reply_markup=get_categories_keyboard(db)
        )
        await state.set_state(UserStates.choosing_category)
    elif message.text == "🛒 Savat":
        from handlers.cart import show_cart
        await show_cart(message, state)
        
