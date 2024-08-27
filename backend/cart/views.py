from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import Cart, CartItem, Product
from .serializers import CartSerializer, CartItemSerializer    
from .models import Cart, CartItem, Payment
from .serializers import CartSerializer, PaymentSerializer
from .paypal import create_payment
from django.shortcuts import get_object_or_404
import paypalrestsdk
import logging

from .models import Cart, CartItem, Payment
from .serializers import CartSerializer, PaymentSerializer
from .paypal import create_payment

logger = logging.getLogger(__name__)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def get_or_create(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            raise ValidationError({'product_id': 'This field is required.'})

        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError
        except ValueError:
            raise ValidationError({'quantity': 'Must be a positive integer.'})

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    
    @action(detail=True, methods=['get'])
    def total(self, request, pk=None):
        cart = self.get_object()
        total = sum(item.product.price * item.quantity for item in cart.items.all())
        return Response({'total': total})

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        cart = self.get_object()
        cart.items.all().delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

        
    @action(detail=True, methods=['post'])
    def remove_from_cart(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item_id')

        if not item_id:
            raise ValidationError({'item_id': 'This field is required.'})

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.delete()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item_id')
        new_quantity = request.data.get('quantity')

        if not item_id:
            return Response({'item_id': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not new_quantity:
            return Response({'quantity': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_quantity = int(new_quantity)
            if new_quantity < 1:
                raise ValueError
        except ValueError:
            return Response({'quantity': 'Must be a positive integer.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.quantity = new_quantity
            item.save()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    
    @action(detail=True, methods=['get'])
    def total(self, request, pk=None):
        cart = self.get_object()
        return Response({'total': cart.get_total_price()})
    

    @action(detail=True, methods=['post'])
    def create_payment(self, request, pk=None):
            cart = self.get_object()
            try:
                payment = create_payment(cart)
                if payment:
                    db_payment = Payment.objects.create(
                        user=request.user,
                        cart=cart,
                        payment_id=payment.id,
                        amount=cart.get_total_price()
                    )
                    return Response({
                        "payment_id": payment.id,
                        "approval_url": next(link.href for link in payment.links if link.rel == "approval_url")
                    })
                else:
                    logger.error(f"Failed to create PayPal payment for cart {cart.id}")
                    return Response({"error": "Failed to create payment"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.exception(f"Error creating PayPal payment for cart {cart.id}: {str(e)}")
                return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def execute_payment(self, request):
            payment_id = request.query_params.get('paymentId')
            payer_id = request.query_params.get('PayerID')
            try:
                payment = paypalrestsdk.Payment.find(payment_id)
                if payment.execute({"payer_id": payer_id}):
                    db_payment = get_object_or_404(Payment, payment_id=payment_id)
                    db_payment.status = 'completed'
                    db_payment.save()
                    
                    cart = db_payment.cart
                    cart.items.all().delete()
                    
                    return Response({"message": "Payment executed successfully"})
                else:
                    logger.error(f"Failed to execute PayPal payment {payment_id}")
                    return Response({"error": "Failed to execute payment"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.exception(f"Error executing PayPal payment {payment_id}: {str(e)}")
                return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['get'])
    def cancel_payment(self, request):
            payment_id = request.query_params.get('paymentId')
            db_payment = get_object_or_404(Payment, payment_id=payment_id)
            db_payment.status = 'cancelled'
            db_payment.save()
            return Response({"message": "Payment cancelled"})

   
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)