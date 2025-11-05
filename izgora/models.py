from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from users.models import User
from utils.compressor import optimize_image_to_webp


def check_image_size(image):
    if image.size > 10 * 1024 * 1024:
        raise ValidationError("The image is too long")


class Category(models.Model):
    DISPLAY_CHOICES = [
        ('emoji', 'Show Emoji'),
        ('image', 'Show Image'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='categories', null=True, blank=True)
    name = models.CharField(max_length=200)
    emoji = models.CharField(max_length=200, null=True, blank=True)
    order = models.IntegerField(default=1)
    image = models.ImageField(upload_to='category/', validators=[
        FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'svg', 'webp', 'JPG', 'JPEG', 'PNG', 'SVG', 'WEBP', 'heic',
                                'heif']),
        check_image_size], blank=True,
                              null=True)
    display_type = models.CharField(max_length=10, choices=DISPLAY_CHOICES, default='emoji',
                                    help_text="Choose whether to show emoji or image")
    slug = models.SlugField(max_length=200, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def clean(self):
        base_slug = slugify(self.name) if self.name else ''
        if not base_slug:
            raise ValidationError({'name': 'Name cannot be empty.'})

        slug_to_check = base_slug
        qs = Category.objects.filter(user=self.user, slug=slug_to_check).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({'slug': 'This slug already exists for this user.'})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name) if self.name else ''
        self.full_clean()

        if self.image and not str(self.image.name).endswith('.webp'):
            optimized_image = optimize_image_to_webp(self.image, quality=80)
            self.image.save(optimized_image.name, optimized_image, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = 'category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        constraints = [
            models.UniqueConstraint(fields=['user', 'slug'], name='unique_user_slug')
        ]


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


class ProductVariants(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='variant_products')
    size = models.CharField(max_length=100, null=True, blank=True)
    diametr = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)

    def __str__(self):
        return str(self.size and self.diametr and self.price)


class ProductImage(models.Model):
    image = models.ImageField(upload_to='product/', validators=[
        FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'svg', 'webp', 'JPG', 'JPEG', 'PNG', 'SVG', 'WEBP', 'heic',
                                'heif']),
        check_image_size])
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.image and not str(self.image.name).endswith('.webp'):
            # Funksiyani chaqiramiz 👇
            optimized_image = optimize_image_to_webp(self.image, quality=80)
            self.image.save(optimized_image.name, optimized_image, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} | {self.id}"

    class Meta:
        db_table = 'productimage'
        verbose_name = 'Product image'
        verbose_name_plural = 'Product images'


class HomeImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, )
    title = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='homeimage/', validators=[
        FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'svg', 'webp', 'JPG', 'JPEG', 'PNG', 'SVG', 'WEBP', 'heic',
                                'heif']),
        check_image_size])

    def save(self, *args, **kwargs):
        if self.image and not str(self.image.name).endswith('.webp'):
            optimized_image = optimize_image_to_webp(self.image, quality=80)
            self.image.save(optimized_image.name, optimized_image, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'homeimage'
        verbose_name = 'Home image'
        verbose_name_plural = 'Home images'


class LogoImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='logoimage/', validators=[
        FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'svg', 'webp', 'JPG', 'JPEG', 'PNG', 'SVG', 'WEBP', 'heic',
                                'heif']),
        check_image_size])

    def save(self, *args, **kwargs):
        if self.image and not str(self.image.name).endswith('.webp'):
            optimized_image = optimize_image_to_webp(self.image, quality=80)
            self.image.save(optimized_image.name, optimized_image, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'logoimage'
        verbose_name = 'Logo image'
        verbose_name_plural = 'Logo images'


class SplashImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='splashimage/', validators=[
        FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'svg', 'webp', 'JPG', 'JPEG', 'PNG', 'SVG', 'WEBP', 'heic',
                                'heif']),
        check_image_size])

    def save(self, *args, **kwargs):
        if self.image and not str(self.image.name).endswith('.webp'):
            optimized_image = optimize_image_to_webp(self.image, quality=80)
            self.image.save(optimized_image.name, optimized_image, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'splashimage'
        verbose_name = 'Splash image'
        verbose_name_plural = 'Splash images'
