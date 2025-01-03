# Generated by Django 5.0.3 on 2024-12-29 09:24

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0007_alter_vendor_vendor_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vendor",
            name="vendor_id",
            field=models.UUIDField(
                default=uuid.UUID("fcd50bcb-5500-44e4-9e86-511730141c44"),
                null=True,
                unique=True,
            ),
        ),
    ]
