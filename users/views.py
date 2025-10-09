from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.generics import UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, LogoutSerializer, MeSerializer
from .models import User
from .serializers import UserListSerializer


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
