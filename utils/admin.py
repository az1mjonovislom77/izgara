from django.contrib import admin
from django.utils.safestring import mark_safe
from django.core.files.base import ContentFile
import qrcode
from io import BytesIO

from utils.models import QrCode


class QrCodeInline(admin.TabularInline):
    model = QrCode
    extra = 0
    fields = ('link', 'qr_preview', 'created')
    readonly_fields = ('qr_preview',)

    def qr_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="100" height="100" style="border:1px solid #ccc; border-radius:5px;" />'
            )
        return "QR mavjud emas"

    qr_preview.short_description = "QR Preview"

    def save_model(self, request, obj, form, change):
        if obj.link:
            qr_image = qrcode.make(obj.link)
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            file_name = f"qr_{obj.user.username}_{obj.id or 'new'}.png"
            obj.image.save(file_name, ContentFile(buffer.getvalue()), save=False)
        super().save_model(request, obj, form, change)
