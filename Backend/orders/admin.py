from django.contrib import admin
from .models import Order,OrderItem 
# Register your models here.
admin.site.register([Order,OrderItem])