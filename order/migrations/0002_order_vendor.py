# Generated by Django 5.0.3 on 2024-12-29 09:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0001_initial"),
        ("product", "0005_alter_vendor_vendor_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="vendor",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="vendor_orders",
                to="product.vendor",
            ),
        ),
    ]
