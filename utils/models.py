import uuid
import qrcode
from django.core.exceptions import ValidationError
from django.db import models
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone

from users.models import User


class QrCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qrcodes')
    link = models.URLField(max_length=500)
    image = models.ImageField(upload_to='qrcodes', blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        existing = QrCode.objects.filter(user=self.user, link=self.link).exclude(pk=self.pk)
        if existing.exists():
            raise ValidationError("Bu foydalanuvchi uchun bu link bo‘yicha QR kod allaqachon mavjud!")

        if not self.image and self.link:
            qr_img = qrcode.make(self.link)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            file_name = f"qr_{self.user.username}_{uuid.uuid4().hex[:8]}.png"
            self.image.save(file_name, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR for {self.user.username}"
