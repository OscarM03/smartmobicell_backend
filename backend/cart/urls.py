from pathlib import Path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('execute-payment/', CartViewSet.as_view({'get': 'execute_payment'}), name='execute_payment'),
    path('cancel-payment/', CartViewSet.as_view({'get': 'cancel_payment'}), name='cancel_payment'),
]