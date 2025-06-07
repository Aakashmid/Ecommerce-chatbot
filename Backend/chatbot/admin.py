from django.contrib import admin
from .models import ChatbotSession,ChatMessage
# Register your models here.


admin.site.register([ChatbotSession,ChatMessage])
