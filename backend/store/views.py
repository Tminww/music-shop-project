import django
from django.contrib.auth.models import User
from django.http import HttpResponse
from store.models import Address, Cart, Category, Liked, Order, Product
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
from django.db.models import F
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator  # for Class Based Views

# from django.shortcuts import render, get_object_or_404
# from django.db.models import Q
# from .models import Category, Product

# Create your views here.


def home(request):
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    context = {
        "categories": categories,
        "products": products,
    }
    print(context)
    print(categories[0].slug)
    return render(request, "store/index.html", context)


def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(
        is_active=True, category=product.category
    )
    context = {
        "product": product,
        "related_products": related_products,
    }
    return render(request, "store/detail.html", context)


def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    print("CATEGORIES", *categories)
    return render(request, "store/categories.html", {"categories": categories})


def contacts(request):
    context = {}
    return render(request, "store/contacts.html", context)


def catalog_products(request):

    slug = request.GET.get("slug")

    if slug:
        category = get_object_or_404(Category, slug=slug)
    else:
        category = "Все товары"
        print("SLUG", slug)

    sorting = request.GET.get("sorting")
    min_price = request.GET.get("min-price")
    max_price = request.GET.get("max-price")

    print("PRICE", min_price, max_price)
    print("SORTING", sorting)
    # Получаем продукты данной категории
    products = Product.objects.filter(is_active=True)

    # Применяем сортировку, если она указана
    if sorting == "low-high":
        products = products.order_by("price")
    elif sorting == "high-low":
        products = products.order_by("-price")

    # Применяем фильтрацию по ценовому диапазону, если параметры заданы
    if min_price and max_price:
        products = products.filter(price__range=(min_price, max_price))
        print("FILTERED_PRODUCTS", products)

    categories = Category.objects.filter(is_active=True)

    context = {
        "category": category,
        "products": products,
        "categories": categories,
        "sorting": sorting,
        "min_price": min_price,
        "max_price": max_price,
    }

    return render(request, "store/catalog_products.html", context)


# Authentication Starts Here


class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, "account/register.html", {"form": form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, "account/register.html", {"form": form})


@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(
        request, "account/profile.html", {"addresses": addresses, "orders": orders}
    )


@method_decorator(login_required, name="dispatch")
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, "account/add_address.html", {"form": form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user = request.user
            locality = form.cleaned_data["locality"]
            city = form.cleaned_data["city"]
            state = form.cleaned_data["state"]
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect("store:profile")


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect("store:profile")


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get("prod_id")
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()

    return redirect(request.META.get("HTTP_REFERER"))


@login_required
def add_to_liked(request):
    user = request.user
    product_id = request.GET.get("prod_id")
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_liked = Liked.objects.filter(product=product_id, user=user)
    if not item_already_in_liked:
        Liked(user=user, product=product).save()


@login_required
def cart(request):
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

    context = {
        "cart_products": cart_products,
        "amount": amount,
        "shipping_amount": shipping_amount,
        "total_amount": amount + shipping_amount,
        "addresses": addresses,
    }
    return render(request, "store/cart.html", context)


@login_required
def remove_cart(request, cart_id):
    if request.method == "GET":
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect("store:cart")


@login_required
def plus_cart(request, cart_id):
    if request.method == "GET":
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect("store:cart")


@login_required
def minus_cart(request, cart_id):
    if request.method == "GET":
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect("store:cart")


@login_required
def checkout(request):
    user = request.user
    address_id = request.GET.get("address")

    address = get_object_or_404(Address, id=address_id)
    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Order(user=user, address=address, product=c.product, quantity=c.quantity).save()
        # And Deleting from Cart
        c.delete()
    return redirect("store:orders")


@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by("-ordered_date")
    return render(request, "store/orders.html", {"orders": all_orders})


def shop(request):
    return render(request, "store/shop.html")


def test(request):
    return render(request, "store/test.html")
