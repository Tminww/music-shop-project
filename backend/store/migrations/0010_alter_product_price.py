# Generated by Django 3.2.3 on 2024-05-25 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_order_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=0, max_digits=8, verbose_name='Цена товара'),
        ),
    ]