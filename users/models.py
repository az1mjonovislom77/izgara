import uuid
import qrcode
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group, Permission
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import BaseUserManager
from io import BytesIO
from django.core.files import File
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Login is required")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class UserRoles(models.TextChoices):
        ADMIN = 'a', "admin"
        CAFE = 'c', "cafe"

    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=100)
    secret_key = models.UUIDField(default=uuid.uuid4, unique=True)
    username = models.CharField(max_length=100, unique=True)
    payment_status = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=UserRoles.choices)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True, verbose_name='groups',
                                    help_text='The groups this user belongs to')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions_set', blank=True,
                                              verbose_name='user permissions',
                                              help_text='Specific permissions for this user.', )
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['name', 'role']
    objects = UserManager()

    def __str__(self):
        return self.name

    def get_tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    class Meta:
        db_table = 'user'


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
