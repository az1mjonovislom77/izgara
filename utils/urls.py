from django.urls import path
from .views import QrCodeGenerateAPIView, QrCodesByUserDownloadAPIView

urlpatterns = [
    path('generate/', QrCodeGenerateAPIView.as_view(), name='qr-generate'),
    path('download/<int:user_id>/', QrCodesByUserDownloadAPIView.as_view(), name='qrcode-download-by-user'),
]
