from django.urls import path
from .views import LoginAPIView, LogOutAPIView, MeAPIView, MeEditAPIView, DeleteAccountAPIView

urlpatterns = [
    path("login/", LoginAPIView.as_view()),
    path("logout/", LogOutAPIView.as_view()),
    path("me/", MeAPIView.as_view()),
    path("me-edit/", MeEditAPIView.as_view()),
    path("delete-account/", DeleteAccountAPIView.as_view()),
]
