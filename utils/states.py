from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    main_menu = State()
    choosing_main_category = State()    # ✅ Yangi: Asosiy kategoriya tanlash
    choosing_subcategory = State()      # ✅ Yangi: Subkategoriya tanlash
    viewing_products = State()
    choosing_product = State()
    choosing_color = State()
    choosing_size = State()
    entering_quantity = State()
    cart = State()
    ordering_phone = State()
    ordering_location = State()
    ordering_payment = State()
    ordering_confirmation = State()
    choosing_custom_color = State()
    choosing_custom_size = State()

class AdminStates(StatesGroup):
    main_menu = State()
    adding_product_name = State()
    adding_product_description = State()
    adding_product_price = State()
    adding_product_category = State()
    adding_product_image = State()
    adding_product_colors = State()
    adding_product_sizes = State()
    adding_product_min_quantity = State()
    adding_custom_color = State()
    adding_custom_size = State()
    broadcasting_message = State()
    confirming_broadcast = State()
    # ✅ YANGI: Mahsulotlarni boshqarish state'lari qo'shildi
    managing_products = State()
    deleting_product = State()