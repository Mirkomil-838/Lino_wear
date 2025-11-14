from .start import router as start_router
from .categories import router as categories_router
from .cart import router as cart_router
from .admin import router as admin_router

__all__ = ['start_router', 'categories_router', 'cart_router', 'admin_router']