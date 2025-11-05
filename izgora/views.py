from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from users.models import User
from .models import Category, Product, HomeImage, LogoImage, SplashImage
from .serializers import (CategorySerializer, ProductSerializer, AdminCategorySerializer, ProductByCategorySerializer,
                          CategoryStatusSerializer, HomeImageSerializer, LogoImageSerializer, SplashImageSerializer)


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


@extend_schema(tags=['Category'])
class CategoryStatusAPIView(APIView):
    serializer_class = CategoryStatusSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = CategoryStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        status_value = serializer.validated_data['status']

        if user.role == User.UserRoles.CAFE:
            updated_count = Category.objects.filter(user=user).update(display_type=status_value)
            return Response({
                "message": f"Sizning {updated_count} ta kategoriyangiz holati '{status_value}' ga o‘zgartirildi ✅"
            }, status=status.HTTP_200_OK)

        elif user.role == User.UserRoles.ADMIN:
            user_id = serializer.validated_data.get('user_id')
            if not user_id:
                return Response(
                    {"error": "Admin uchun user_id kiritilishi shart."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "Bunday user topilmadi."}, status=status.HTTP_404_NOT_FOUND)

            updated_count = Category.objects.filter(user=target_user).update(display_type=status_value)
            return Response({
                "message": f"{target_user.name} foydalanuvchisining {updated_count} ta kategoriyasi '{status_value}' holatiga o‘zgartirildi ✅"
            }, status=status.HTTP_200_OK)

        else:
            return Response({"error": "Sizga bu amalni bajarish ruxsat etilmagan."},
                            status=status.HTTP_403_FORBIDDEN)


@extend_schema(tags=['Category'])
class AdminCategoryStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = request.user

        if user.role != User.UserRoles.ADMIN:
            return Response({"error": "Faqat admin foydalanuvchilar kirishlari mumkin."},
                            status=status.HTTP_403_FORBIDDEN)

        target_user = get_object_or_404(User, id=user_id)
        categories = Category.objects.filter(user=target_user)

        if not categories.exists():
            return Response({"message": "Bu foydalanuvchida category mavjud emas."},
                            status=status.HTTP_404_NOT_FOUND)

        unique_statuses = list(categories.values_list('display_type', flat=True).distinct())
        status_value = unique_statuses[0] if len(unique_statuses) == 1 else "mixed"

        return Response({
            "status": status_value,
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['Category'])
class CafeCategoryStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != User.UserRoles.CAFE:
            return Response({"error": "Faqat cafe foydalanuvchilar kirishlari mumkin."},
                            status=status.HTTP_403_FORBIDDEN)

        categories = Category.objects.filter(user=user)

        if not categories.exists():
            return Response({"message": "Sizda hali category mavjud emas."},
                            status=status.HTTP_404_NOT_FOUND)

        unique_statuses = list(categories.values_list('display_type', flat=True).distinct())
        status_value = unique_statuses[0] if len(unique_statuses) == 1 else "mixed"

        return Response({
            "status": status_value,
        }, status=status.HTTP_200_OK)


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


@extend_schema(tags=['HomeImage'])
class HomeImageAPIView(APIView):
    serializer_class = HomeImageSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        if user.role == User.UserRoles.ADMIN:
            homeimages = HomeImage.objects.all()
        else:
            homeimages = HomeImage.objects.filter(user=user)

        serializer = HomeImageSerializer(homeimages, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        data = request.data.copy()

        if user.role == User.UserRoles.ADMIN:
            pass
        else:
            data['user'] = user.id

        serializer = HomeImageSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['HomeImageDetail'])
class HomeImageDetailAPIView(APIView):
    serializer_class = HomeImageSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        home = get_object_or_404(HomeImage, pk=pk)
        serializer = HomeImageSerializer(home, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        homeimage = get_object_or_404(HomeImage, pk=pk)
        serializer = HomeImageSerializer(homeimage, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        homeimage = get_object_or_404(HomeImage, pk=pk)
        homeimage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['LogoImage'])
class LogoImageAPIView(APIView):
    serializer_class = LogoImageSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        if user.role == User.UserRoles.ADMIN:
            logoimage = LogoImage.objects.all()
        else:
            logoimage = LogoImage.objects.filter(user=user)

        serializer = LogoImageSerializer(logoimage, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        data = request.data.copy()

        if user.role == User.UserRoles.ADMIN:
            pass
        else:
            data['user'] = user.id

        serializer = LogoImageSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['LogoImageDetail'])
class LogoImageDetailAPIView(APIView):
    serializer_class = LogoImageSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        logoimage = get_object_or_404(LogoImage, pk=pk)
        serializer = LogoImageSerializer(logoimage, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        logoimage = get_object_or_404(HomeImage, pk=pk)
        serializer = LogoImageSerializer(logoimage, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        logoimage = get_object_or_404(LogoImage, pk=pk)
        logoimage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['SplashImage'])
class SplashImageAPIView(APIView):
    serializer_class = SplashImageSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        if user.role == User.UserRoles.ADMIN:
            splashimages = SplashImage.objects.all()
        else:
            splashimages = SplashImage.objects.filter(user=user)

        serializer = SplashImageSerializer(splashimages, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        data = request.data.copy()

        if user.role == User.UserRoles.ADMIN:
            pass
        else:
            data['user'] = user.id

        serializer = SplashImageSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['SplashImageDetail'])
class SplashImageDetailAPIView(APIView):
    serializer_class = SplashImageSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        splashimage = get_object_or_404(SplashImage, pk=pk)
        serializer = SplashImageSerializer(splashimage, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        splashimage = get_object_or_404(HomeImage, pk=pk)
        serializer = SplashImageSerializer(splashimage, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        splashimage = get_object_or_404(SplashImage, pk=pk)
        splashimage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
