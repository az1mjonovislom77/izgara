from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from users.models import User


def check_image_size(image):
    if image.size > 4 * 1024 * 1024:
        raise ValidationError("The image is too long")


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='categories', null=True, blank=True)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images/category/', validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg', 'webp']),
        check_image_size], blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = 'category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    rating = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        db_table = 'product'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class ProductImage(models.Model):
    image = models.ImageField(upload_to='images/product/', validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg', 'webp', 'heic', 'heif']),
        check_image_size])

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product} | {self.id}"

    class Meta:
        db_table = 'productimage'
        verbose_name = 'Product image'
        verbose_name_plural = 'Product images'
