import decimal
from .models import Address, Category, Cart, Liked


def store_menu(request):
    categories = Category.objects.filter(is_active=True)
    context = {
        "categories_menu": categories,
    }
    return context


def cart_menu(request):
    if request.user.is_authenticated:

        user = request.user
        cart_products = Cart.objects.filter(user=user)

        # Display Total on Cart Page
        amount = decimal.Decimal(0)
        shipping_amount = decimal.Decimal(10)
        # using list comprehension to calculate total amount based on quantity and shipping
        cp = [p for p in Cart.objects.all() if p.user == user]
        if cp:
            for p in cp:
                temp_amount = p.quantity * p.product.price
                amount += temp_amount

        # Customer Addresses
        addresses = Address.objects.filter(user=user)

        percentage_discount = 5

        cart_items = Cart.objects.filter(user=request.user)
        liked_items = Liked.objects.filter(user=request.user)

        cart_items = [items.quantity for items in cart_items]

        # request.session["cartMenu"] = False
        # request.session.modified = True

        context = {
            "cart_items": sum(cart_items),
            "liked_items": liked_items,
            "cart_products": cart_products,
            "active": "cart",
            "cartMenu": False,
            "amount": int(amount),
            "shipping_amount": shipping_amount,
            "discount": int((amount / 100) * percentage_discount),
            "total_amount": int(amount) - int((amount / 100) * percentage_discount),
            "addresses": addresses,
        }
        print(context)
    else:
        context = {}
    return context
