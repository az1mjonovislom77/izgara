import qrcode
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.core.files.base import ContentFile
from io import BytesIO
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import QrCode


@admin.register(QrCode)
class QrCodeAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'link', 'preview_qr', 'total_scans', 'daily_scans', 'monthly_scans', 'yearly_scans', 'created'
    )
    readonly_fields = ('preview_qr', 'total_scans', 'daily_scans', 'monthly_scans', 'yearly_scans')
    search_fields = ('user__username', 'link')
    list_filter = ('created',)

    def preview_qr(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" height="80" />')
        return "QR mavjud emas"
    preview_qr.short_description = "QR Ko‘rinishi"

    def total_scans(self, obj):
        return obj.scans.count()
    total_scans.short_description = "Umumiy skanlar"

    def daily_scans(self, obj):
        today = timezone.now().date()
        return obj.scans.filter(created__date=today).count()
    daily_scans.short_description = "Kunlik skanlar"

    def monthly_scans(self, obj):
        now = timezone.now()
        return obj.scans.filter(created__year=now.year, created__month=now.month).count()
    monthly_scans.short_description = "Oylik skanlar"

    def yearly_scans(self, obj):
        now = timezone.now()
        return obj.scans.filter(created__year=now.year).count()
    yearly_scans.short_description = "Yillik skanlar"

    def save_model(self, request, obj, form, change):
        # Faqat yangi QR yaratishda tekshirish
        if not change and QrCode.objects.filter(user=obj.user).exists():
            raise ValidationError(f"{obj.user} uchun QR kod allaqachon mavjud!")

        # QR rasm yaratish
        if obj.link and not obj.image:
            qr_image = qrcode.make(obj.link)
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            file_name = f"qr_{obj.user.username}.png"
            obj.image.save(file_name, ContentFile(buffer.getvalue()), save=False)

        super().save_model(request, obj, form, change)
