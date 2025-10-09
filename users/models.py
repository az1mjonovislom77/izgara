from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group, Permission
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import BaseUserManager


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

    title = models.CharField(max_length=100)
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
    REQUIRED_FIELDS = ['title', 'role']
    objects = UserManager()

    def __str__(self):
        return self.title

    def get_tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    class Meta:
        db_table = 'user'
