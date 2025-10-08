from django.contrib import admin
from izgora.models import (
    Category, Product, ProductImage, CategoryImages
)


class ProductImageTabular(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'name', 'slug',)


@admin.register(CategoryImages)
class CategoryImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'image')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'category', 'title', 'price',
    )
    inlines = (ProductImageTabular,)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
