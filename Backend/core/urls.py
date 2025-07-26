
from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.urls import path,include
from products.views import ProductViewSet,CategoryViewSet
from rest_framework.routers import DefaultRouter 
router = DefaultRouter()



router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/chatbot/', include('chatbot.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/carts/', include('carts.urls')),
    path('api/', include(router.urls)),
    path('api/', include('users.urls')),

]
