import sys
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image
import pillow_heif
from django.core.files.uploadedfile import InMemoryUploadedFile

pillow_heif.register_heif_opener()


def optimize_image_to_webp(image_field, quality: int = 80, max_width=1200, ) -> ContentFile:
    # Rasmni ochamiz
    img = Image.open(image_field)
    img = img.convert('RGB')  # WebP uchun zarur

    # 1️⃣ Rasm kengligini kamaytirish
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int(float(img.height) * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    # 2️⃣ WebP formatida siqish
    buffer = BytesIO()
    img.save(buffer, format='WEBP', quality=quality)
    buffer.seek(0)

    # 3️⃣ Yangi nom yaratish
    file_name = image_field.name.rsplit('.', 1)[0] + '.webp'

    new_image = InMemoryUploadedFile(
        buffer,  # fayl ma'lumotlari
        'ImageField',  # maydon nomi
        file_name,  # fayl nomi
        'image/webp',  # MIME turi
        sys.getsizeof(buffer),  # fayl hajmi
        None  # charset
    )

    return new_image
