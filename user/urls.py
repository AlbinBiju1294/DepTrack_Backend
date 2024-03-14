from django.urls import path,include
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='registration'),
    path("userslist/", UserListView.as_view(), name="userslist"),
    path("user/", SingleUserView.as_view(), name="userfetch"),
    path('login/', ObtainJWTWithEmail.as_view(), name='token_obtain_email'),
]