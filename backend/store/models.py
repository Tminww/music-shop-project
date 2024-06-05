# from django.conf import settings
from django.db import models

from django.contrib.auth.models import User

# from django.contrib.auth.models import AbstractUser
from django.db import models


# class CustomUser(AbstractUser):
#     phone_number = models.CharField(max_length=15, blank=True, null=True)
#     date_of_birthday = models.DateField(auto_now=False, verbose_name="Дата рождения")

#     def __str__(self):
#         return self.username


# Create your models here.
class Address(models.Model):
    user = models.ForeignKey(
        User, verbose_name="Пользователь", on_delete=models.CASCADE
    )
    locality = models.CharField(max_length=150, verbose_name="Город")
    city = models.CharField(max_length=150, verbose_name="Улица")
    state = models.CharField(max_length=150, verbose_name="Дом")

    class Meta:
        verbose_name_plural = "Адреса"

    def __str__(self):
        return self.locality


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name="Имя категории")
    slug = models.SlugField(
        max_length=55, unique=True, verbose_name="Web имя категории"
    )
    description = models.TextField(blank=True, verbose_name="Описание категории")
    category_image = models.ImageField(
        upload_to="category",
        blank=True,
        null=True,
        verbose_name="Изображение категории",
    )
    is_active = models.BooleanField(verbose_name="Активность")
    is_featured = models.BooleanField(verbose_name="Избранное")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        verbose_name_plural = "Категории"
        ordering = ("-created_at",)

    # def __str__(self):
    #     return self.title


class Product(models.Model):
    title = models.CharField(max_length=150, verbose_name="Название продукта")
    slug = models.SlugField(max_length=160, verbose_name="Web Название продукта")
    sku = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Уникальный идентификатор продукта(ID)",
    )
    short_description = models.TextField(verbose_name="Краткое описание")
    detail_description = models.TextField(
        blank=True, null=True, verbose_name="Подробное описание"
    )
    product_image = models.ImageField(
        upload_to="product", blank=True, null=True, verbose_name="Изображение продукта"
    )
    price = models.DecimalField(
        max_digits=8, decimal_places=0, verbose_name="Цена товара"
    )
    category = models.ForeignKey(
        Category, verbose_name="Категория продукта", on_delete=models.CASCADE
    )
    is_active = models.BooleanField(verbose_name="Активен")
    is_featured = models.BooleanField(verbose_name="Избранное")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        verbose_name_plural = "Товары"
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, verbose_name="Product", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        verbose_name_plural = "Товары в заказе"

    def __str__(self):
        return str(self.user)

    # Creating Model Property to calculate Quantity x Price
    @property
    def total_price(self):
        return self.quantity * self.product.price


class Liked(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, verbose_name="Product", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        verbose_name_plural = "Понравившиеся товары"


STATUS_CHOICES = (
    ("Обрабатывается", "Обрабатывается"),
    ("Принял", "Принял"),
    ("Упакован", "Упакован"),
    ("В пути", "В пути"),
    ("Доставлен", "Доставлен"),
    ("Отменен", "Отменен"),
)


class Order(models.Model):
    user = models.ForeignKey(
        User, verbose_name="Пользователь", on_delete=models.CASCADE
    )
    uuid = models.TextField(null=True, verbose_name="uuid")
    address = models.ForeignKey(
        Address, null=True, verbose_name="Адрес доставки", on_delete=models.CASCADE
    )
    price = models.IntegerField(null=True, verbose_name="Цена заказа")
    product = models.ForeignKey(
        Product, verbose_name="Продукт", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    ordered_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    delivery_date = models.DateTimeField(
        auto_now_add=False, null=True, verbose_name="Дата доставки"
    )
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=50,
        default="Обрабатывается",
        verbose_name="Статус",
    )

    class Meta:
        verbose_name_plural = "Заказы"
