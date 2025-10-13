from django.urls import path
from .views import QrCodeGenerateAPIView, QrCodesByUserDownloadAPIView, QrCodeUpdateAPIView, QrCodeGetAPIView, \
    QrCodeDeleteAPIView

urlpatterns = [
    path('generate/', QrCodeGenerateAPIView.as_view(), name='qr-generate'),
    path('download/<int:user_id>/', QrCodesByUserDownloadAPIView.as_view(), name='qrcode-download-by-user'),
    path('update/<int:pk>/', QrCodeUpdateAPIView.as_view(), name='qr-update'),
    path('all/', QrCodeGetAPIView.as_view(), name='qr-all'),
    path('delete/<int:pk>/', QrCodeDeleteAPIView.as_view(), name='qr-delete'),
]
