from rest_framework import serializers
from .models import Order, OrderItem
from django.contrib.auth import get_user_model
from users.models import Address
from products.serializers import ProductSerializer
from products.models import Product
from users.serializers import UserSerializer, AddressSerializer

User = get_user_model()

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price', 'total', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    
    # Write-only fields for creating an order
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    shipping_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source='shipping_address',
        write_only=True
    )
    billing_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source='billing_address',
        write_only=True,
        required=False
    )
    
    # Additional read-only properties
    is_paid = serializers.BooleanField(read_only=True)
    is_shipped = serializers.BooleanField(read_only=True)
    is_delivered = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_id', 'order_number', 'status', 'payment_method',
            'shipping_address', 'shipping_address_id', 'billing_address', 'billing_address_id',
            'subtotal', 'shipping_cost', 'tax', 'total', 'discount', 'notes',
            'tracking_number', 'created_at', 'updated_at', 'paid_at', 'shipped_at',
            'delivered_at', 'items', 'is_paid', 'is_shipped', 'is_delivered'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at']