from django.urls import path
from .views import (
    CategoryListCreateAPIView,
    CategoryDetailAPIView,
    ProductListCreateAPIView,
    ProductDetailAPIView, AdminCategoryCreateAPIView, CategoryBySecretKeyAPIView, ProductCategoryBySecretKeyAPIView,
    CategoryByUserIdAPIView, CategoryStatusAPIView, )

urlpatterns = [
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('categories/set-display/', CategoryStatusAPIView.as_view(), name='category-set-display'),
    path('admin/categories/', AdminCategoryCreateAPIView.as_view(), name='admin-category-create'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    path('secret-key/categories/', CategoryBySecretKeyAPIView.as_view(), name='categories_by_secret_key'),
    path('secret-key/category-products/', ProductCategoryBySecretKeyAPIView.as_view(),
         name='category_products_by_secret_key'),
    path('categories/by-user/<int:user_id>/', CategoryByUserIdAPIView.as_view(), name='categories-by-user'),

    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
]
