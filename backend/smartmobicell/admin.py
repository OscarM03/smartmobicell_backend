from django.contrib import admin
from .models import Order, CartItem, OrderItems, Category, Profile, Product, DisplayProduct, Laptop, OfferProduct, PickOfTheWeek

class OrderItemsInline(admin.TabularInline):
    model = OrderItems
    extra = 0 
    readonly_fields = ('product', 'quantity')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'email', 'phone_number', 'total_amount',  'shippingoption', 'created_at')
    inlines = [OrderItemsInline]

admin.site.register(Category)
admin.site.register(Profile)
admin.site.register(Product)
admin.site.register(DisplayProduct)
admin.site.register(OfferProduct)
admin.site.register(PickOfTheWeek)
admin.site.register(Laptop)
admin.site.register(CartItem)
admin.site.register(OrderItems)
admin.site.register(Order, OrderAdmin)
