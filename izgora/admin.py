from django.contrib import admin
from izgora.models import Category, Product, ProductImage, ProductVariants


class ProductImageTabular(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantTabular(admin.TabularInline):
    model = ProductVariants
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'user', 'name', 'slug',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'title')
    inlines = (ProductImageTabular, ProductVariantTabular)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
