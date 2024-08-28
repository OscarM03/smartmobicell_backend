from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, Order, OrderItems, Product, CartItem, OfferProduct, DisplayProduct, PickOfTheWeek, Laptop

# class ProfileSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(source='user.username')
#     email = serializers.EmailField(source='user.email')

#     class Meta:
#         model = Profile
#         fields = ['username', 'email', 'name', 'profile_image', 'address', 'phone_number']

#     # def update(self, instance, validated_data):
#     #     user_data = validated_data.pop('user', {})

#     #     user = instance.user
#     #     username = user_data.get('username')
#     #     email = user_data.get('email')

#     #     if username:
#     #         user.username = username
#     #         user.save()
#     #     if email:
#     #         user.email = email
#     #         user.save()

#     #     return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ["id", "username", "password", "confirm_password", "email"]
        extra_kwargs = {
            "password": {"write_only": True},
            "confirm_password": {"write_only": True}
        }
    def __init__(self, *args, **kwargs):
        exclude_fields = kwargs.pop('exclude_fields', None)
        super().__init__(*args, **kwargs)
        if exclude_fields:
            for field in exclude_fields:
                self.fields.pop(field)

    def validate(self, data):
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)
        user = User.objects.create_user(**validated_data)
        # send_verification_email(user)
        return user

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OfferProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferProduct
        fields = '__all__'

class DisplayProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisplayProduct
        fields = '__all__'

class PickOfTheWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickOfTheWeek
        fields = '__all__'

class LaptopsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laptop
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'
        depth = 1

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(exclude_fields=['password', 'confirm_password'])
    class Meta:
        model = Profile
        fields = ['user', 'firstname', 'lastname', 'profile_image', 'address', 'phone_number']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        for attr, value in user_data.items():
            print(f"Updating {attr} to {value}")  # Debug statement
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
    
class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemsSerializer(many=True)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'email', 'phone_number', 'county',  'shippingoption', 'address', 'total_amount', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItems.objects.create(order=order, **item_data)
        return order