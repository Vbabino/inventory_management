# Generated by Django 5.1.1 on 2024-09-24 09:22

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "inventorymanager",
            "0003_alter_orderitem_quantity_alter_orderitem_unit_price",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="order_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
