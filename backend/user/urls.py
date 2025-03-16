from django.urls import path
from .views import GetAcessToken, UserAuthAPI, UserLogoutAPI, UserRegisterAPI, ValidateToken
urlpatterns = [
    path('register/', UserRegisterAPI.as_view(), name='user-register'),
    path('auth/', UserAuthAPI.as_view(), name='user-auth'),
    path('get-access-token/', GetAcessToken.as_view(), name='user-auth'),
    path('validate-token/', ValidateToken.as_view(), name='validate-token'),
    path('logout/', UserLogoutAPI.as_view(), name='user-auth')
]