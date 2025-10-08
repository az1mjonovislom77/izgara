from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Category, Product, ProductImage, CategoryImages
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    CategoryImagesSerializer
)


@extend_schema(tags=['Category'])
class CategoryListCreateAPIView(APIView):
    serializer_class = CategorySerializer
    def get(self, request):
        categories = Category.objects.all().order_by('-created')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['CategoryDetail'])
class CategoryDetailAPIView(APIView):
    serializer_class = CategorySerializer
    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Product'])
class ProductListCreateAPIView(APIView):
    serializer_class = ProductSerializer
    def get(self, request):
        products = Product.objects.select_related('category').prefetch_related('productimage_set').all().order_by(
            '-created')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['ProductDetail'])
class ProductDetailAPIView(APIView):
    serializer_class = ProductSerializer
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Product'])
class ProductImageListCreateAPIView(APIView):
    def get(self, request):
        images = ProductImage.objects.all()
        serializer = ProductImageSerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Category'])
class CategoryImagesListCreateAPIView(APIView):
    def get(self, request):
        images = CategoryImages.objects.all()
        serializer = CategoryImagesSerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategoryImagesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
