# Generated by Django 5.0.3 on 2024-12-29 10:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0003_cartproduct_vendor"),
        ("product", "0010_alter_vendor_vendor_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cartproduct",
            name="vendor",
        ),
        migrations.AddField(
            model_name="cart",
            name="vendor",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cart_product_vendor",
                to="product.vendor",
            ),
        ),
    ]