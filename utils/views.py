import os
import zipfile
from django.urls import reverse
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import QrCodeSerializer, QrCodeUpdateSerializer, QrCodeGetSerializer
from io import BytesIO
from django.shortcuts import redirect, get_object_or_404
from .models import QrCode, User, QrScanLog


@extend_schema(tags=['QR Code'])
class QrCodeGenerateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QrCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        qr = serializer.save()
        qr.link = request.build_absolute_uri(reverse('qr-scan', args=[qr.id]))
        qr.save(update_fields=['link'])

        return Response(self.serializer_class(qr, context={'request': request}).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['QR Code'])
class QrCodeUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QrCodeUpdateSerializer

    def put(self, request, pk):
        qr = get_object_or_404(QrCode, pk=pk)

        if request.user.role == User.UserRoles.CAFE and qr.user != request.user:
            return Response(
                {"error": "Siz faqat o‘zingizning QR kodingizni tahrirlay olasiz."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = QrCodeUpdateSerializer(qr, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['QR Code'])
class QrCodeGetAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QrCodeGetSerializer

    def get(self, request):
        if request.user.role == User.UserRoles.CAFE:
            qr = QrCode.objects.filter(user_id=request.user.id)
        elif request.user.role == User.UserRoles.ADMIN:
            qr = QrCode.objects.all()
        else:
            return Response(
                {"error": "Sizda QR kodlarni ko‘rish uchun ruxsat yo‘q."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = QrCodeGetSerializer(qr, many=True, context={'request': request})
        return Response(serializer.data)


@extend_schema(tags=['QR Code'])
class QrCodeDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        qr = get_object_or_404(QrCode, pk=pk)
        qr.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['QR Code'])
class QrCodesByUserDownloadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        current_user = request.user
        if current_user.role == User.UserRoles.ADMIN:
            if not user_id:
                return Response(
                    {"error": "Admin user_id ni kiritishi kerak!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            target_user = get_object_or_404(User, id=user_id)

        elif current_user.role == User.UserRoles.CAFE:
            if user_id and user_id != current_user.id:
                return Response(
                    {"error": "Siz faqat o‘zingizga tegishli QR kodni yuklab olishingiz mumkin!"},
                    status=status.HTTP_403_FORBIDDEN
                )
            target_user = current_user

        else:
            return Response(
                {"error": "Sizda QR kodlarni yuklab olish uchun ruxsat yo‘q!"},
                status=status.HTTP_403_FORBIDDEN
            )

        qrcodes = QrCode.objects.filter(user=target_user)
        if not qrcodes.exists():
            return Response(
                {"detail": "Bu foydalanuvchida QR kodlar mavjud emas."},
                status=status.HTTP_404_NOT_FOUND
            )

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w") as zip_file:
            for qr in qrcodes:
                if qr.image and os.path.exists(qr.image.path):
                    filename = os.path.basename(qr.image.path)
                    zip_file.write(qr.image.path, arcname=filename)

        buffer.seek(0)
        zip_filename = f"{target_user.username}_qrcodes.zip"
        response = HttpResponse(buffer, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{zip_filename}"'
        return response


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def qr_scan_view(request, qr_id):
    qr = get_object_or_404(QrCode, id=qr_id)
    ip = get_client_ip(request)

    # Scan log yaratish
    QrScanLog.objects.create(qr_code=qr, ip=ip)

    # Scan count update
    qr.scan_count += 1
    qr.last_scanned_ip = ip
    qr.save(update_fields=['scan_count', 'last_scanned_ip'])

    return redirect(qr.link)
