from rest_framework import serializers
from users.models import User
from .models import Category, Product, ProductImage, ProductVariants
from django.utils.text import slugify
import json


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'emoji', 'order']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        name = attrs.get('name', getattr(self.instance, 'name', None))
        if not name or not user or user.is_anonymous:
            return attrs

        from django.utils.text import slugify
        slug_val = slugify(name)
        qs = Category.objects.filter(user=user, slug=slug_val)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError({
                'slug': 'This slug already exists for this user.'
            })

        return attrs


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None


class ProductVariantSerializer(serializers.ModelSerializer):
    diameter = serializers.IntegerField(source='diametr')

    class Meta:
        model = ProductVariants
        fields = ['size', 'diameter', 'price']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(source='productimage_set', many=True, required=False, read_only=True)
    variants = ProductVariantSerializer(source='variant_products', many=True, required=False)
    category_name = serializers.CharField(source='category.name', read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    images_post = serializers.ListField(child=serializers.ImageField(), required=False, write_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'created', 'category', 'category_name',
            'images', 'rating', 'price', 'variants', 'images_post'
        ]

    def get_variants(self, obj):
        return [
            {
                "size": v.size,
                "diameter": v.diametr,
                "price": v.price
            }
            for v in obj.variant_products.all()
        ]

    def create(self, validated_data):
        request = self.context.get('request')

        variants_raw = request.data.get('variants')
        variants_data = []
        if variants_raw:
            try:
                variants_data = json.loads(variants_raw)
            except Exception as e:
                print("❌ Variant JSON parsing error:", e)

        images_post = validated_data.pop('images_post', [])

        product = Product.objects.create(**validated_data)

        for image in images_post:
            ProductImage.objects.create(product=product, image=image)

        for variant in variants_data:
            ProductVariants.objects.create(product=product, size=variant.get('size'), diametr=variant.get('diameter'),
                                           price=variant.get('price'))

        return product

    def get_price(self, obj):
        try:
            if hasattr(obj, 'variant_products') and obj.variant_products.exists():
                return None
        except Exception:
            return obj.price
        return obj.price


class AdminCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Category
        fields = ['user', 'name', 'image', 'emoji', 'order', 'created']
        read_only_fields = ['slug', 'created']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None

    def validate(self, attrs):
        name = attrs.get('name', getattr(self.instance, 'name', None))
        user = attrs.get('user', getattr(self.instance, 'user', None))

        if not name:
            return attrs

        slug_val = slugify(name)
        qs = Category.objects.filter(user=user, slug=slug_val)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError({
                'slug': 'This slug already exists for this user.'
            })

        return attrs


class ProductByCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'emoji', 'image', 'created', 'order', 'products']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None
