from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 
                  'profile_picture', 'date_of_birth', 'password', 'confirm_password',
                  'date_joined', 'last_login', 'is_active']
        read_only_fields = ['date_joined', 'last_login', 'is_active']
    
    def validate(self, data):
        # Validate password match when creating a new user
        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({"confirm_password": "Passwords don't match."})
            # Remove confirm_password from the data
            data.pop('confirm_password')
        return data
    
    def create(self, validated_data):
        # Create a new user
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        # Update user data
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance




class AddressSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    
    class Meta:
        model = Address
        fields = [
            'id', 'user', 'user_id', 'address_type', 'full_name', 
            'address_line1', 'address_line2', 'city', 'state', 
            'postal_code', 'country', 'phone_number', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        # Ensure address_type is valid
        if 'address_type' in data and data['address_type'] not in dict(Address.ADDRESS_TYPES):
            raise serializers.ValidationError({"address_type": "Invalid address type."})
        return data
    
    def create(self, validated_data):
        # Create a new address
        address = Address.objects.create(**validated_data)
        return address
    
    def update(self, instance, validated_data):
        # Update address data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance