from .consumers import ChatConsumer
from django.urls import path

websocket_urlpatterns = [
    path('ws/chatbot/message/<str:session_id>/', ChatConsumer.as_asgi()),
]