from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('session', views.ChatbotSessionViewSet, basename="session")


urlpatterns = [
    path('session/<str:session_id>/messages', views.ChatMessageView.as_view(), name='session-message'),
    path('',include(router.urls))
]
