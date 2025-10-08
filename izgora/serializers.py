from rest_framework import serializers
from .models import Category, Product, ProductImage, CategoryImages


class CategoryImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryImages
        fields = ['id', 'image']


class CategorySerializer(serializers.ModelSerializer):
    images = CategoryImagesSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'slug', 'created', 'images']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(source='productimage_set', many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'price',
            'created',
            'category',
            'category_name',
            'images',
        ]
