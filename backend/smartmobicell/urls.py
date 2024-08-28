from django.urls import path
from .views import HomePageView, UserProfileView, AddToCartView, CreateOrderView
urlpatterns = [
    path('userprofile/', UserProfileView.as_view(), name='user-profile'),
    path('cart/', AddToCartView.as_view(), name='cart'),
    path('cart/delete/<str:id>/', AddToCartView.as_view(), name='cart-item-delete'),
    path('cart/orders/', CreateOrderView.as_view(), name='create-order'),
    path('<str:section>/', HomePageView.as_view(), name='home-page'),
    path('<str:section>/<str:id>/', HomePageView.as_view(), name='home-page-detail'),
    
]