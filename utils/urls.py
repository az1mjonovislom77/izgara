from django.urls import path
from .views import QrCodeGenerateAPIView, QrCodesByUserDownloadAPIView, QrCodeUpdateAPIView, QrCodeGetAPIView, \
    QrCodeDeleteAPIView, qr_scan_view

urlpatterns = [
    path('admin-download/<int:user_id>/', QrCodesByUserDownloadAPIView.as_view(), name='qrcode-download-by-user'),
    path('download/', QrCodesByUserDownloadAPIView.as_view(), name='qrcode-download-self'),
    path('all/', QrCodeGetAPIView.as_view(), name='qr-all'),
    path('generate/', QrCodeGenerateAPIView.as_view(), name='qr-generate'),
    path('update/<int:pk>/', QrCodeUpdateAPIView.as_view(), name='qr-update'),
    path('delete/<int:pk>/', QrCodeDeleteAPIView.as_view(), name='qr-delete'),
    path('qr/<int:qr_id>/scan/', qr_scan_view, name='qr-scan'),
]
