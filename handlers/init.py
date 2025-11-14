from .start import router as start_router
from .categories import router as categories_router
from .cart import router as cart_router
from .admin import router as admin_router
from .back_handler import router as back_router
from .unknown import router as unknown_router
from .orders import router as orders_router  # ✅ Buyurtmalar routerini qo'shamiz

__all__ = ['start_router', 'categories_router', 'cart_router', 'admin_router', 'back_router', 'unknown_router', 'orders_router']