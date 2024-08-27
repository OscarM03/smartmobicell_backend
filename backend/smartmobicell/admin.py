from django.contrib import admin
from .models import Category, Product, DisplayProduct, Laptop, OfferProduct, PickOfTheWeek

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(DisplayProduct)
admin.site.register(OfferProduct)
admin.site.register(PickOfTheWeek)
admin.site.register(Laptop)
