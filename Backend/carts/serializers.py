from rest_framework import serializers
from .models import CartItem
from products.serializers import ProductSerializer
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'user', 'created_at', 'updated_at', 'total_price']
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_total_price(self, obj):
        if obj.product.discount_price:
            return obj.product.discount_price * obj.quantity
        return obj.product.price * obj.quantity
    
    def create(self, validated_data):
        # Get the current user from the request
        user = self.context['request'].user
        
        # Check if the item already exists in the cart
        try:
            cart_item = CartItem.objects.get(
                user=user,
                product=validated_data['product']
            )
            # Update quantity if item exists
            cart_item.quantity += validated_data.get('quantity', 1)
            cart_item.save()
            return cart_item
        except CartItem.DoesNotExist:
            # Create new cart item
            return CartItem.objects.create(
                user=user,
                **validated_data
            )