import os
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.generics import UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, LogoutSerializer, MeSerializer, UserCreateSerializer, UserUpdateSerializer, \
    QrCodeSerializer
from .models import User, QrCode
from .serializers import UserListSerializer
import zipfile
from io import BytesIO


@extend_schema(tags=['Login'])
class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            "success": True,
            "message": "Login muvaffaqiyatli bajarildi",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
            }
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['Login'])
class LogOutAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Profile'])
class MeAPIView(RetrieveAPIView):
    serializer_class = MeSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Profile'])
class MeEditAPIView(UpdateAPIView):
    serializer_class = MeSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    http_method_names = ['put']

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Profile'])
class DeleteAccountAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        user = get_object_or_404(User, username=request.user)
        if user.is_active:
            user.is_active = False
            user.save()
            return Response({'message': 'Account has been deleted'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'Account not found'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['User'])
class UserListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_superuser and user.role != User.UserRoles.ADMIN:
            return Response({"detail": "Ruxsat yo'q"}, status=status.HTTP_403_FORBIDDEN)

        users = User.objects.all().order_by('username')
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)


@extend_schema(tags=['User'])
class UserCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserCreateSerializer

    def post(self, request):
        user = request.user

        if not user.is_superuser and user.role != User.UserRoles.ADMIN:
            return Response({"detail": "Ruxsat yo'q"}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['UserDetail'])
class UserDetailAPIView(APIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserListSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response({'detail': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['QR Code'])
class QrCodeGenerateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QrCodeSerializer

    def post(self, request):
        user_id = request.data.get('user')
        link = request.data.get('link')

        if not user_id or not link:
            return Response({'error': 'user va link kerak'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User topilmadi'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role != User.UserRoles.ADMIN:
            return Response({'error': 'Sizda ruxsat yo‘q'}, status=status.HTTP_403_FORBIDDEN)

        qr = QrCode.objects.create(user=user, link=link)
        serializer = QrCodeSerializer(qr, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
