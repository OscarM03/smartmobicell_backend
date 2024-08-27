from rest_framework import serializers
from smartmobicell.models import Product
from .models import Cart, CartItem, Payment

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'item_total']

    def get_item_total(self, obj):
        return obj.get_item_price()

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total']

    def get_total(self, obj):
        return obj.get_total_price()
    
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_id', 'status', 'amount', 'created_at', 'updated_at']