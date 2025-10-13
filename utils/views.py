import os
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import QrCodeSerializer, QrCodeUpdateSerializer, QrCodeGetSerializer
from .models import User, QrCode
import zipfile
from io import BytesIO


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

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        qrcodes = QrCode.objects.filter(user=user)

        if not qrcodes.exists():
            return Response({"detail": "Bu foydalanuvchida QR kodlar mavjud emas"}, status=status.HTTP_404_NOT_FOUND)

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w") as zip_file:
            for qr in qrcodes:
                if qr.image and os.path.exists(qr.image.path):
                    filename = os.path.basename(qr.image.path)
                    zip_file.write(qr.image.path, arcname=filename)

        buffer.seek(0)
        zip_filename = f"{user.username}_qrcodes.zip"
        response = HttpResponse(buffer, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{zip_filename}"'
        return response
