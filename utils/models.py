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

    total_scans = models.PositiveIntegerField(default=0)
    daily_scans = models.PositiveIntegerField(default=0)
    monthly_scans = models.PositiveIntegerField(default=0)
    yearly_scans = models.PositiveIntegerField(default=0)
    last_scan = models.DateTimeField(null=True, blank=True)

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

    def increment_scans(self):
        now = timezone.now()

        if not self.last_scan or self.last_scan.date() != now.date():
            self.daily_scans = 0
        if not self.last_scan or self.last_scan.year != now.year or self.last_scan.month != now.month:
            self.monthly_scans = 0
        if not self.last_scan or self.last_scan.year != now.year:
            self.yearly_scans = 0

        self.total_scans += 1
        self.daily_scans += 1
        self.monthly_scans += 1
        self.yearly_scans += 1
        self.last_scan = now
        self.save()

    def __str__(self):
        return f"QR for {self.user.username}"
