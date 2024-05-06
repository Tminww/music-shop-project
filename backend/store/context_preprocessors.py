from .models import Category, Cart, Liked


def store_menu(request):
    categories = Category.objects.filter(is_active=True)
    context = {
        "categories_menu": categories,
    }
    return context


def cart_menu(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        liked_items = Liked.objects.filter(user=request.user)

        cart_items = [items.quantity for items in cart_items]
        context = {
            "cart_items": sum(cart_items),
            "liked_items": liked_items,
        }
        print(context)
    else:
        context = {}
    return context
