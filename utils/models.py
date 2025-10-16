import uuid
import qrcode
from django.core.exceptions import ValidationError
from django.db import models
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone

from users.models import User


class QrCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='qrcode')
    link = models.CharField(max_length=500)
    image = models.ImageField(upload_to='qrcodes', blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "QR Code"
        verbose_name_plural = "QR Codes"

    def clean(self):
        if not self.pk and QrCode.objects.filter(user=self.user).exists():
            raise ValidationError("Bu foydalanuvchi uchun QR kod allaqachon yaratilgan!")

    def save(self, *args, **kwargs):
        self.clean()

        if not self.image and self.link:
            qr_img = qrcode.make(self.link)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            file_name = f"qr_{self.user.username}_{uuid.uuid4().hex[:8]}.png"
            self.image.save(file_name, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR for {self.user.username}"


class QrScan(models.Model):
    qr_code = models.ForeignKey(QrCode, related_name='scans', on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "QR Scan"
        verbose_name_plural = "QR Scans"

    def __str__(self):
        return f"Skan - {self.qr_code.user.username} ({self.created_at.date()})"
