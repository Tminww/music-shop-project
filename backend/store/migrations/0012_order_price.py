# Generated by Django 3.2.3 on 2024-05-25 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_order_delivery_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='price',
            field=models.IntegerField(null=True, verbose_name='Цена заказа'),
        ),
    ]
