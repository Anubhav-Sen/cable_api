from django.urls import path
from cable_api.views import user_views, chat_views, message_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', user_views.users_view, name='users'),
    path('users/<int:user_id>/', user_views.user_view, name='user'),
    path('chats/', chat_views.chats_view, name='chats'),
    path('chats/<int:chat_id>/', chat_views.chat_view, name='chat'),
    path('chats/<int:chat_id>/messages/', message_views.messages_view, name='messages'),
    path('chats/<int:chat_id>/messages/<int:message_id>/', message_views.message_view, name='message')
]