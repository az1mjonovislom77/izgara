from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from users.models import User
from .models import Category, Product
from .serializers import (CategorySerializer, ProductSerializer, AdminCategorySerializer, ProductByCategorySerializer, )


@extend_schema(tags=['Category'])
class CategoryListCreateAPIView(APIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == User.UserRoles.ADMIN:
            categories = Category.objects.all().order_by('-created')
        else:
            categories = Category.objects.filter(user=user).order_by('-created')

        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Product'])
class ProductListCreateAPIView(APIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == User.UserRoles.ADMIN:
            products = Product.objects.select_related('category').prefetch_related('productimage_set',
                                                                                   'variant_products').all().order_by(
                '-created')
        else:
            products = Product.objects.select_related('category').prefetch_related('productimage_set',
                                                                                   'variant_products').filter(
                category__user=user
            ).order_by('-created')

        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={'request': request, 'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['CategoryDetail'])
class CategoryDetailAPIView(APIView):
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['ProductDetail'])
class ProductDetailAPIView(APIView):
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Category'])
class AdminCategoryCreateAPIView(APIView):
    serializer_class = AdminCategorySerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        if not user.is_authenticated or user.role != User.UserRoles.ADMIN:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        serializer = AdminCategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Category'])
class CategoryBySecretKeyAPIView(APIView):

    def get(self, request, *args, **kwargs):
        secret_key = request.query_params.get('secret_key')

        if not secret_key:
            return Response(
                {"detail": "secret_key kiritilmadi. Masalan: ?secret_key=<uuid>"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(secret_key=secret_key)
        except User.DoesNotExist:
            return Response(
                {"detail": "Bunday secret_key topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        categories = Category.objects.filter(user=user)
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['Category'])
class ProductCategoryBySecretKeyAPIView(APIView):

    def get(self, request, *args, **kwargs):
        secret_key = request.query_params.get('secret_key')
        if not secret_key:
            return Response({"error": "secret_key kiritilmadi"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(secret_key=secret_key)
        except User.DoesNotExist:
            return Response({"error": "User topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        categories = Category.objects.filter(user=user)
        serializer = ProductByCategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)


@extend_schema(tags=['Category'])
class CategoryByUserIdAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        categories = Category.objects.filter(user=user)
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
