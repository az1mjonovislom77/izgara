from django.urls import path
from .views import (
    CategoryListCreateAPIView,
    CategoryDetailAPIView,
    ProductListCreateAPIView,
    ProductDetailAPIView,
    ProductImageListCreateAPIView,
    CategoryImagesListCreateAPIView, AdminCategoryCreateAPIView,
)

urlpatterns = [
    # Category
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('admin/categories/', AdminCategoryCreateAPIView.as_view(), name='admin-category-create'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),

    # Product
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
]
