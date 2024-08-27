from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Product, Profile, DisplayProduct, OfferProduct, PickOfTheWeek, Laptop
from .serializers import (
    UserSerializer, ProductSerializer, 
    DisplayProductSerializer, OfferProductSerializer, 
    PickOfTheWeekSerializer, LaptopsSerializer, ProfileSerializer
)

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UserProfileView(APIView):

    def get(self, request):
            user = request.user
            profile = get_object_or_404(Profile, user=user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        profile = get_object_or_404(Profile, user=user)

        data = request.data
        
        serializer = ProfileSerializer(profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
        

class HomePageView(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []       # Disable permission checks

    
    section_mapping = {
        'products': (Product, ProductSerializer),
        'displayproducts': (DisplayProduct, DisplayProductSerializer),
        'offerproduct': (OfferProduct, OfferProductSerializer),
        'pickoftheweek': (PickOfTheWeek, PickOfTheWeekSerializer),
        'laptops': (Laptop, LaptopsSerializer),
        'accessories': (Product, ProductSerializer)
    }

    def get(self, request, section, id=None):
        if section not in self.section_mapping:
            return Response({'error': 'Invalid section'}, status=400)

        model, serializer_class = self.section_mapping[section]

        
        if id is not None:
            if section == 'accessories':
                product = get_object_or_404(model, id=id, is_accessory=True)
            else:
                product = get_object_or_404(model, id=id)
            serializer = serializer_class(product)
            return Response(serializer.data)

        
        query = request.GET.get('q', '')  
        products = model.objects.all()


        if section == 'accessories':
            products = products.filter(is_accessory=True)
        if query:
            if section == 'products':
                products = products.filter(
                    Q(name__icontains=query) |
                    Q(brand__icontains=query) |
                    Q(category__name__icontains=query)
                )



        if section == 'offerproduct':
            product = products.order_by('-created_at').first()  # Get the latest product
            serializer = serializer_class(product) if product else serializer_class([])  # Serialize if item exists
        elif section == 'pickoftheweek':
            products = products.order_by('-created_at')[:2]  # Get the top 2 products
            serializer = serializer_class(products, many=True)  # Serialize the list of items
        else:
            serializer = serializer_class(products, many=True)  # Default case

        return Response(serializer.data)

