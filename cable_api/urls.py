from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', views.users_view, name='users'),
    path('users/<int:user_id>/', views.user_view, name='user'),
    path('chats/', views.chats_view, name='chats'),
    path('chats/<int:chat_id>', views.chat_view, name='chat'),
]