import uuid
import django
from django.contrib.auth import get_user_model
from yookassa import Configuration, Settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from store.models import Address, Cart, Category, Liked, Order, Product
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm, LoginForm
from django.contrib import messages
from django.views import View
from django.db.models import F
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator  # for Class Based Views
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect

from yookassa import Payment
from itertools import chain


def home(request):
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True, is_featured=True)[:4]

    if request.user.is_authenticated:
        liked_items = Liked.objects.filter(user=request.user)
        liked_items = [item.product.pk for item in liked_items]
    else:
        liked_items = None

    context = {
        "categories": categories,
        "products": products,
        "liked_id": liked_items,
        "sorting": "popularity",
    }
    print(context)
    print(categories[0].slug)
    return render(request, "store/index.html", context)


@login_required
def address(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    context = {
        "addresses": addresses,
        "orders": orders,
        "active": "address",
    }
    return render(request, "account/address.html", context)
    pass


@login_required
def add_address(request):
    form = AddressForm(request.POST)
    print(form.is_valid())
    locality = request.POST.get("town")
    city = request.POST.get("street")
    state = request.POST.get("home")

    user = request.user

    reg = Address(user=user, locality=locality, city=city, state=state)
    reg.save()
    messages.success(request, "New Address Added Successfully.")
    return redirect("store:address")


@login_required
def settings(request):

    context = {
        "active": "settings",
    }
    return render(request, "account/settings.html", context)


@login_required
def liked(request):
    user = request.user

    liked_products_id = [
        product.product_id for product in Liked.objects.filter(user=user)
    ]

    liked_products = Product.objects.filter(is_active=True, id__in=liked_products_id)

    sorting = request.GET.get("sorting")

    # Применяем сортировку, если она указана
    if sorting == "low-high":
        liked_products = liked_products.order_by("price")
    elif sorting == "high-low":
        liked_products = liked_products.order_by("-price")

    context = {
        "sorting": sorting,
        "liked_products": liked_products,
        "active": "liked",
        "liked_id": liked_products_id,
    }
    return render(request, "account/liked.html", context)


@login_required
def orders(request):

    orders_uuids = set(
        Order.objects.filter(user=request.user).values_list("uuid", flat=True)
    )

    order = Order.objects.filter(user=request.user).order_by("-ordered_date")
    print(orders_uuids)
    all_orders = []
    prices = []
    for uuid in orders_uuids:
        order = Order.objects.filter(user=request.user, uuid=uuid).order_by(
            "-ordered_date"
        )
        price = 0

        for product in order:
            print(product)
            # for duplicate in range(1, product.quantity):
            #     order = chain(order, product)

            price += product.product.price * product.quantity
            prices.append(price)

        all_orders.append(order)

    print(prices)

    context = {
        "orders": all_orders,
        "active": "orders",
        "prices": prices,
    }

    return render(request, "account/orders.html", context)


def user_login_controller(request):
    if request.method == "POST":
        username_or_email = request.POST.get("user-login")
        user_password = request.POST.get("user-login-password")

        categories = Category.objects.filter(is_active=True)
        products = Product.objects.filter(is_active=True, is_featured=True)[:4]

        if request.user.is_authenticated:
            liked_items = Liked.objects.filter(user=request.user)
            liked_items = [item.product.pk for item in liked_items]
        else:
            liked_items = None

        context = {
            "categories": categories,
            "products": products,
            "liked_id": liked_items,
            "sorting": "popularity",
            "previous_page": "login",
        }

        user = None
        if username_or_email and user_password:
            # Попытка аутентификации по имени пользователя
            user = authenticate(username=username_or_email, password=user_password)
            if not user:
                # Попытка аутентификации по email
                try:
                    user_temp = User.objects.get(email=username_or_email)
                    user = authenticate(
                        username=user_temp.username, password=user_password
                    )

                except User.DoesNotExist:
                    pass

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("store:home")
                # return HttpResponse("Authenticated successfully")
            else:

                messages.warning(request=request, message="Неверный логин или пароль")
                return render(request, "store/index.html", context)
        else:
            messages.warning(request=request, message="Неверный логин или пароль")
            return render(request, "store/index.html", context)

    # redirect(request.META.get("HTTP_REFERER"))

    # return render(request, 'account/login.html', {'form': form})


@csrf_protect
def user_register_controller(request):
    if request.method == "POST":
        username = request.POST.get("user-register")
        user_password = request.POST.get("user-register-password")
        user_password2 = request.POST.get("user-register-password2")
        user_email = request.POST.get("email")
        # user_first_name = request.POST.get("first-name")
        # user_last_name = request.POST.get("last-name")
        # user_surname = request.POST.get("surname")
        # user_phone_number = request.POST.get("phone-number")
        # user_birth_date = request.POST.get("birth-date")

        categories = Category.objects.filter(is_active=True)
        products = Product.objects.filter(is_active=True, is_featured=True)[:4]

        if request.user.is_authenticated:
            liked_items = Liked.objects.filter(user=request.user)
            liked_items = [item.product.pk for item in liked_items]
        else:
            liked_items = None

        context = {
            "categories": categories,
            "products": products,
            "liked_id": liked_items,
            "sorting": "popularity",
            "previous_page": "register",
        }

        if user_password == user_password2:

            user_already_exists = User.objects.filter(username=username)
            if user_already_exists:
                messages.warning(request=request, message="Имя пользователя занято")
                return render(request, "store/index.html", context)
            else:

                user = User.objects.create_user(
                    username=username,
                    # first_name=user_first_name,
                    # last_name=user_last_name,
                    password=user_password,
                    email=user_email,
                )
                # user.profile.surname = user_surname
                # user.profile.phone_number = user_phone_number
                # user.profile.birth_date = user_birth_date
                user.save()
                login(request, user)
                return redirect("store:home")

        else:
            messages.warning(request=request, message="Пароли не совпадают")
            return render(request, "store/index.html", context)

    return render(request, "store/index.html", context)

    #     print(username)
    #     print(user_password)
    #     user = authenticate(username=username, password=user_password)

    #     print(user)

    #     if user is not None:
    #         if user.is_active:
    #             login(request, user)
    #             return redirect("store:home")
    #             # return HttpResponse("Authenticated successfully")
    #         else:
    #             return HttpResponse("Disabled account")
    #     else:
    #         return HttpResponse("Invalid login")

    # redirect(request.META.get("HTTP_REFERER"))


def detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    popular_products = Product.objects.filter(is_active=True, is_featured=True)[:4]

    if request.user.is_authenticated:
        liked_products_id = [
            product.product_id for product in Liked.objects.filter(user=request.user)
        ]
    else:
        liked_products_id = None

    related_products = Product.objects.exclude(id=product.id).filter(
        is_active=True, category=product.category
    )
    context = {
        "product": product,
        "liked_id": liked_products_id,
        "popular_products": popular_products,
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

    slug = request.GET.getlist("slug")

    print("slug_params", slug)
    if "all" not in slug:
        queryset = Category.objects.in_bulk(slug, field_name="slug")
        print("queryset", queryset)
        category = Category.objects.filter(slug__in=slug)
        print("CATEG", category)
        # category = get_object_or_404(Category, in slug=slug)
        # Получаем продукты данной категории
        # queryset = Product.objects.in_bulk(category, category.pk)
        cat_id = [cat.pk for cat in category]

        products = Product.objects.filter(is_active=True, category_id__in=cat_id)

        print("PROD", products)
    else:
        category = "Все товары"
        slug = ["all"]
        products = Product.objects.filter(is_active=True)
        print("PROD", products)
        print("SLUG", slug)

    if request.user.is_authenticated:
        liked_items = Liked.objects.filter(user=request.user)
        liked_items = [item.product.pk for item in liked_items]
    else:
        liked_items = None

    sorting = request.GET.get("sorting")

    min_price = request.GET.get("min-price")

    max_price = request.GET.get("max-price")

    print("MIN_PRICE", min_price)
    print("MAX_PRICE", max_price)

    print("PRICE", min_price, max_price)
    print("SORTING", sorting)

    # Применяем сортировку, если она указана
    if sorting == "low-high":
        products = products.order_by("price")
    elif sorting == "high-low":
        products = products.order_by("-price")

    # Применяем фильтрацию по ценовому диапазону, если параметры заданы
    if min_price or max_price:
        temp_min_price = min_price
        temp_max_price = max_price

        if not min_price:
            temp_min_price = 0
        if not max_price:
            temp_max_price = 99999999999999
        products = products.filter(price__range=(temp_min_price, temp_max_price))
        print("FILTERED_PRODUCTS", products)

    categories = Category.objects.filter(is_active=True)

    context = {
        "category": category,
        "products": products,
        "liked_id": liked_items,
        "categories": categories,
        "sorting": sorting,
        "min_price": min_price,
        "max_price": max_price,
        "slug": slug,
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
    context = {
        "addresses": addresses,
        "orders": orders,
        "active": "profile",
    }
    return render(request, "account/profile.html", context)


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
    return redirect("store:address")


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get("prod_id")
    print(
        "product_id",
        product_id,
    )
    product = get_object_or_404(Product, id=product_id)
    print(product.id)
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
    else:
        c = get_object_or_404(Liked, user=user, product=product)
        c.delete()

    return redirect(request.META.get("HTTP_REFERER"))


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

    percentage_discount = 5

    context = {
        "cart_products": cart_products,
        "active": "cart",
        "amount": int(amount),
        "shipping_amount": shipping_amount,
        "discount": int((amount / 100) * percentage_discount),
        "total_amount": int(amount) - int((amount / 100) * percentage_discount),
        "addresses": addresses,
    }
    return render(request, "account/cart.html", context)


@login_required
def clear_cart(request):
    if request.method == "GET":

        # c = get_object_or_404(Cart, user=request.user)
        c = Cart.objects.filter(user=request.user)
        c.delete()
        messages.success(request, "Product removed from Cart.")

    return redirect("store:cart")


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
def update_quantity_product_in_cart(request, cart_id):
    if request.method == "GET":
        count = request.GET.get("count")
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity = count
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

    amount: int = 0
    percentage_discount = 5
    cp = [p for p in Cart.objects.all() if p.user == user]
    if cp:
        for p in cp:
            temp_amount = p.quantity * p.product.price
            amount += temp_amount

    total_amount = int(amount) - int((amount / 100) * percentage_discount)

    res = Payment.create(
        {
            "amount": {"value": f"{int(total_amount)}", "currency": "RUB"},
            "confirmation": {"type": "embedded"},
            "capture": 1,
            "description": f"Заказ №{uuid.uuid4()}",
        }
    )

    context = {
        "confirmation_token": res.confirmation.confirmation_token,
    }

    return render(request, "payments/payment.html", context)


@login_required
def after_checkout(request):

    try:
        address_id = request.GET.get("address")
        address = get_object_or_404(Address, id=address_id)
    except:
        address_id = None
        address = None
    print(address_id)

    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=request.user)
    current_order = None

    order_uuid = uuid.uuid4()

    amount: int = 0
    percentage_discount = 5
    cp = [p for p in Cart.objects.all() if p.user == request.user]
    if cp:
        for p in cp:
            temp_amount = p.quantity * p.product.price
            amount += temp_amount

    total_amount = int(amount) - int((amount / 100) * percentage_discount)

    for c in cart:
        # Saving all the products from Cart to Order
        for i in range(c.quantity):

            current_order = Order(
                user=request.user,
                uuid=order_uuid,
                address=address,
                product=c.product,
                quantity=1,
                price=total_amount,
            )
            current_order.save()
        # And Deleting from Cart
        c.delete()

    return redirect("store:orders")


@login_required
def change_info(request):
    if request.method == "POST":

        user_confirmation_password = request.POST.get("user-confirmation-password")

        user = authenticate(
            username=request.user.username, password=user_confirmation_password
        )
        context = {
            "active": "settings",
            "previous_page": "settings",
        }

        if user is not None:
            if user.is_active:
                print(request.POST)

                if request.POST.get("first-name"):
                    user.first_name = request.POST.get("first-name")

                if request.POST.get("last-name"):
                    user.last_name = request.POST.get("last-name")

                if request.POST.get("surname"):
                    user.profile.surname = request.POST.get("surname")

                if request.POST.get("phone-number"):
                    user.profile.phone_number = request.POST.get("phone-number")

                tmp = request.POST.get("birth-date")
                print(f"{tmp}")

                if request.POST.get("birth-date"):

                    tmp = request.POST.get("birth-date")
                    print(f"{tmp}")
                    user.profile.birth_date = request.POST.get("birth-date")

                if request.POST.get("email"):
                    user.email = request.POST.get("email")

                if request.POST.get("user-new-password"):
                    user.set_password(request.POST.get("user-new-password"))

                user.save()
                login(request, user)
                return redirect("store:settings")
                # return HttpResponse("Authenticated successfully")
        else:
            messages.warning(request=request, message="Неверный пароль")
            return render(request, "account/settings.html", context)
