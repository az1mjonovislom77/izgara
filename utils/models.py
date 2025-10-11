import uuid
import qrcode
from django.db import models
from io import BytesIO
from django.core.files import File
from django.utils import timezone

from users.models import User


class QrCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qrcodes')
    link = models.URLField(max_length=500)
    image = models.ImageField(upload_to='qrcodes', blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.pk:
            old = QrCode.objects.filter(pk=self.pk).first()
            if old and old.link != self.link:
                if old.image:
                    old.image.delete(save=False)
                self.image = None

        if not self.image:
            qr_img = qrcode.make(self.link)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            file_name = f"qr_{self.user.username}_{uuid.uuid4().hex[:8]}.png"
            self.image.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR for {self.user.username}"
