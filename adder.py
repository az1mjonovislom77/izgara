import os
import django
from django.utils.text import slugify

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from izgora.models import Category, Product, ProductImage
from data import data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_DIR, "media", "assets")

if not os.path.exists(ASSETS_PATH):
    raise FileNotFoundError(f"Papka topilmadi: {ASSETS_PATH}")
files_in_folder = os.listdir(ASSETS_PATH)

for item in data:
    category_name = str(item.get("category", "")).strip()
    if not category_name:
        print(f"⚠️ Category nomi bo‘sh, o‘tkazildi: {item.get('name')}")
        continue

    category, created = Category.objects.get_or_create(name=category_name, defaults={"slug": slugify(category_name)})

    image_name = str(item.get("image", "")).strip()
    matched_file = None
    for f in files_in_folder:
        if f.lower().startswith(image_name.lower()) and f.lower().endswith((".jpg", ".jpeg", ".png")):
            matched_file = f
            break

    if not matched_file:
        print(f"⚠️ Fayl topilmadi: {image_name}")
        continue

    product = Product.objects.create(
        category=category,
        title=item.get("name", ""),
        description=item.get("description", ""),
        about=item.get("about", ""),
        price=item.get("price", 0),
        rating=item.get("rating", 0)
    )

    ProductImage.objects.create(
        product=product,
        image=f"assets/{matched_file}"
    )

    print(f"✅ {product.title} -> {category.name}")

print("✅ Barcha ma’lumotlar import qilindi!")
