import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from chatbot.jwt_middleware import JWTAuthMiddleware
from channels.routing import URLRouter
from chatbot.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})