from django.urls import path
from .views import QrCodeGenerateAPIView, QrCodesByUserDownloadAPIView, QrCodeUpdateAPIView, QrCodeGetAPIView, \
    QrCodeDeleteAPIView, QrScanAPIView

urlpatterns = [
    path('admin-download/<int:user_id>/', QrCodesByUserDownloadAPIView.as_view(), name='qrcode-download-by-user'),
    path('download/', QrCodesByUserDownloadAPIView.as_view(), name='qrcode-download-self'),
    path('all/', QrCodeGetAPIView.as_view(), name='qr-all'),
    path('generate/', QrCodeGenerateAPIView.as_view(), name='qr-generate'),
    path('update/<int:pk>/', QrCodeUpdateAPIView.as_view(), name='qr-update'),
    path('delete/<int:pk>/', QrCodeDeleteAPIView.as_view(), name='qr-delete'),
    path('scan/<int:qr_id>/', QrScanAPIView.as_view(), name='qr-scan'),
]
