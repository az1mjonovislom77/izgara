import qrcode
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.core.files.base import ContentFile
from io import BytesIO
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils import timezone

from utils.models import QrCode, QrScan


class QrCodeInline(admin.TabularInline):
    model = QrCode
    extra = 0
    fields = (
        'link', 'qr_preview', 'daily_scans',
        'monthly_scans', 'yearly_scans', 'total_scans', 'created'
    )
    readonly_fields = (
        'qr_preview', 'daily_scans',
        'monthly_scans', 'yearly_scans', 'total_scans'
    )

    def qr_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="100" height="100" style="border:1px solid #ccc; border-radius:5px;" />'
            )
        return "QR mavjud emas"

    qr_preview.short_description = "QR Preview"

    def total_scans(self, obj):
        return obj.scans.count()

    total_scans.short_description = "Umumiy skanlar"

    def daily_scans(self, obj):
        today = timezone.now().date()
        return obj.scans.filter(date=today).count()

    daily_scans.short_description = "Kunlik skanlar"

    def monthly_scans(self, obj):
        today = timezone.now()
        return obj.scans.filter(date__year=today.year, date__month=today.month).count()

    monthly_scans.short_description = "Oylik skanlar"

    def yearly_scans(self, obj):
        today = timezone.now()
        return obj.scans.filter(date__year=today.year).count()

    yearly_scans.short_description = "Yillik skanlar"

    def save_model(self, request, obj, form, change):
        existing_qr = QrCode.objects.filter(user=obj.user)

        if not change and existing_qr.exists():
            messages.error(request, "Bu user uchun QR kod allaqachon mavjud!")
            raise ValidationError("QR code already exists.")

        if obj.link and not obj.image:
            qr_image = qrcode.make(obj.link)
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            file_name = f"qr_{obj.user.username}_{obj.id or 'new'}.png"
            obj.image.save(file_name, ContentFile(buffer.getvalue()), save=False)

        super().save_model(request, obj, form, change)
