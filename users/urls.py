from django.urls import path
from .views import LoginAPIView, LogOutAPIView, MeAPIView, MeEditAPIView, DeleteAccountAPIView, UserListAPIView, \
    UserCreateAPIView, UserDetailAPIView

urlpatterns = [

    path("login/", LoginAPIView.as_view()),
    path("logout/", LogOutAPIView.as_view()),
    path("me/", MeAPIView.as_view()),
    path("me-edit/", MeEditAPIView.as_view()),
    path("delete-account/", DeleteAccountAPIView.as_view()),
    path('all-users/', UserListAPIView.as_view(), name='user-list'),
    path('user-create/', UserCreateAPIView.as_view(), name='user-create'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
]
