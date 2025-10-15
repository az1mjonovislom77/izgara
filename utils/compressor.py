import io, os
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError
import pillow_heif

pillow_heif.register_heif_opener()


def optimize_image_to_webp(image_field, quality: int = 80) -> ContentFile:
    try:
        image = Image.open(image_field)
    except UnidentifiedImageError:
        raise ValidationError("❌ Noto‘g‘ri yoki qo‘llanilmagan rasm formati!")

    image_field.seek(0)
    original_size = len(image_field.read()) / (1024 * 1024)
    image_field.seek(0)
    if image.mode != "RGB":
        image = image.convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="WEBP", quality=quality, optimize=True, method=6)
    buffer.seek(0)

    base_name, _ = os.path.splitext(image_field.name)
    new_filename = f"{base_name}.webp"
    optimized_size = len(buffer.getvalue()) / (1024 * 1024)

    print(f"\n🖼 Rasm optimallashtirildi:")
    print(f"   ▫️ Oldingi hajm: {original_size:.2f} MB")
    print(f"   ▫️ Yangi hajm:    {optimized_size:.2f} MB")
    print(f"   ▫️ Sifat:         {quality}%")

    return ContentFile(buffer.read(), name=new_filename)
