import os
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import QrCodeSerializer
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
