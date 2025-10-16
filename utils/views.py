import hashlib
import os
import uuid
import zipfile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import QrCodeSerializer, QrCodeUpdateSerializer, QrCodeGetSerializer
from .models import User, QrCode, QrScan
from io import BytesIO
from django.utils import timezone


@extend_schema(tags=['QR Code'])
class QrCodeGenerateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QrCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        qr = serializer.save()
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


def make_device_hash(ip: str, user_agent: str, accept_lang: str = "") -> str:
    """IP + user agent (+ ixtiyoriy accept-language) ga sha256."""
    data = f"{ip}||{user_agent or ''}||{accept_lang or ''}"
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


class QrScanAPIView(APIView):
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def post(self, request, qr_id):
        qr_code = get_object_or_404(QrCode, id=qr_id)

        ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:1000]
        device_uuid = request.COOKIES.get('device_uuid')
        created_cookie = False
        if not device_uuid:
            # generate new uuid4 hex
            device_uuid = uuid.uuid4().hex
            created_cookie = True

        today = timezone.now().date()

        scan, created = QrScan.objects.get_or_create(
            qr_code=qr_code,
            device_uuid=device_uuid,
            date=today,
            defaults={
                'ip_address': ip,
                'user_agent': user_agent,
            }
        )

        if not created:
            pass

        stats = {
            "today": QrScan.objects.filter(qr_code=qr_code, date=today).count(),
            "month": QrScan.objects.filter(qr_code=qr_code, date__year=today.year, date__month=today.month).count(),
            "year": QrScan.objects.filter(qr_code=qr_code, date__year=today.year).count(),
            "total_unique": QrScan.objects.filter(qr_code=qr_code).values('device_uuid').distinct().exclude(device_uuid__isnull=True).count()
        }

        message = "Bugungi skan saqlandi" if created else "Bu qurilma bugun allaqachon skan qilgan"

        response_data = {
            "message": message,
            "statistics": stats
        }

        response = Response(response_data, status=status.HTTP_200_OK)
        if created_cookie:
            max_age = 10 * 365 * 24 * 60 * 60
            response.set_cookie(
                'device_uuid',
                device_uuid,
                max_age=max_age,
                httponly=True,
                samesite='Lax'
            )

        return response