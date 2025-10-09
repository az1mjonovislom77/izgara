from rest_framework import serializers

from users.models import User
from .models import Category, Product, ProductImage, CategoryImages


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(source='productimage_set', many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'created', 'category', 'category_name', 'images']


class AdminCategorySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Category
        fields = ['user', 'name', 'created']
        read_only_fields = ['slug', 'created']
