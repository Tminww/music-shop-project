# Generated by Django 3.2.3 on 2024-05-23 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_alter_order_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='uuid',
            field=models.TextField(null=True, verbose_name='uuid'),
        ),
    ]
