import paypalrestsdk
from django.conf import settings

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

def create_payment(cart):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": "http://localhost:8000/cart/execute-payment/",
            "cancel_url": "http://localhost:8000/cart/cancel-payment/"
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": item.product.name,
                    "sku": str(item.product.id),
                    "price": str(item.product.price),
                    "currency": "USD",
                    "quantity": item.quantity
                } for item in cart.items.all()]
            },
            "amount": {
                "total": str(cart.get_total_price()),
                "currency": "USD"
            },
            "description": f"Payment for cart {cart.id}"
        }]
    })

    if payment.create():
        return payment
    else:
        return None