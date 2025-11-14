from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import Category

def init_categories():
    db = SessionLocal()
    
    try:
        # Avval barcha mavjud kategoriyalarni o'chirib tashlaymiz
        db.query(Category).delete()
        
        # Asosiy kategoriyalarni qo'shish
        main_categories = [
            {"name": "Erkaklar", "parent_id": None},
            {"name": "Ayollar", "parent_id": None},
            {"name": "Bolalar", "parent_id": None},
        ]
        
        main_cat_objects = {}
        for cat_data in main_categories:
            category = Category(**cat_data)
            db.add(category)
            db.flush()  # ID ni olish uchun
            main_cat_objects[cat_data["name"]] = category
        
        db.commit()
        
        # Subkategoriyalarni qo'shish
        subcategories_data = [
            # Erkaklar uchun subkategoriyalar
            {"name": "Oyoq kiyim", "parent_id": main_cat_objects["Erkaklar"].id},
            {"name": "Sviter", "parent_id": main_cat_objects["Erkaklar"].id},
            {"name": "Kurtka", "parent_id": main_cat_objects["Erkaklar"].id},
            
            # Ayollar uchun subkategoriyalar
            {"name": "Oyoq kiyim", "parent_id": main_cat_objects["Ayollar"].id},
            {"name": "Sviter", "parent_id": main_cat_objects["Ayollar"].id},
            {"name": "Kurtka", "parent_id": main_cat_objects["Ayollar"].id},
            
            # Bolalar uchun subkategoriyalar
            {"name": "Oyoq kiyim", "parent_id": main_cat_objects["Bolalar"].id},
            {"name": "Sviter", "parent_id": main_cat_objects["Bolalar"].id},
            {"name": "Kurtka", "parent_id": main_cat_objects["Bolalar"].id},
        ]
        
        for subcat_data in subcategories_data:
            subcategory = Category(**subcat_data)
            db.add(subcategory)
        
        db.commit()
        print("Kategoriyalar muvaffaqiyatli qo'shildi!")
        
    except Exception as e:
        print(f"Xatolik: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_categories()