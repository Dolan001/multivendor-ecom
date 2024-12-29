from io import BytesIO
from random import randint

import requests
from django.core.files.base import ContentFile
from PIL import Image

from product.models.models import *


def fabric_data(data_list):
    characteristic_ids = []
    pattern_ids = []
    category_ids = []
    color_ids = []
    fabric = None
    for data in data_list:
        # print(data)
        brand = data.get("brand")
        specification = data.get("specification")
        compositions = data.get("compositions")
        characteristics = data.get("characteristics")
        patterns = data.get("patterns")
        laundry_informations = data.get("laundryInformation")
        available_product_categories = data.get("availableProductCategories")
        color_ways = data.get("colorWays")

        # fabric = Fabric.objects.filter(fabric_id=data["id"])
        # if fabric:
        #     continue
        # else:
        brand, created = Brand.objects.get_or_create(
            name=brand.get("name"), nationality=brand.get("nationality")
        )

        for category in available_product_categories:
            cat, created = Category.objects.get_or_create(
                title=category, category_type="SUB"
            )
            # print(cat)
            category_ids.append(cat.id)

        for characteristic in characteristics:
            char, created = Characteristic.objects.get_or_create(name=characteristic)
            characteristic_ids.append(char.id)

        for pattern in patterns:
            pat, created = Pattern.objects.get_or_create(name=pattern)
            pattern_ids.append(pat.id)
        if data.get("colorWays") == []:
            raise Exception("ColorWays is empty")
        fabric_thumbnail = data.get("colorWays")[0]["thumbnailUrl"]
        # print("fabric_thumbnail", fabric_thumbnail)
        fabric_name = data.get("colorWays")[0]["name"]

        fabric_image = get_image(fabric_thumbnail, fabric_name)

        fabric, created = Fabric.objects.get_or_create(
            fabric_id=data["id"], brand=brand, name=data.get("name")
        )

        fabric.description = data.get("description")
        fabric.thumbnail = fabric_image
        fabric.save()
        fabric.category.set(category_ids)
        fabric.patterns.set(pattern_ids)
        fabric.characteristics.set(characteristic_ids)

        # need fabric instance
        for color_way in color_ways:
            for color in color_way["colors"]:
                col, created = Color.objects.get_or_create(name=color)
                color_ids.append(col.id)

            colorway_thumbnail_url = color_way["thumbnailUrl"]
            image_file = get_image(colorway_thumbnail_url, color_way["name"])

            color_way_instance, created = ColorWay.objects.get_or_create(
                fabric=fabric,
                name=color_way["name"],
            )
            color_way_instance.thumbnail = image_file
            color_way_instance.colors.set(color_ids)
            if color_way_instance.price == float(0):
                price = float(randint(10, 100))
                color_way_instance.price = price
            color_way_instance.save()

            real_fabric_colorway_images = color_way["realFabricColorwayImages"]
            real_fabric_colorway_images_len = len(real_fabric_colorway_images)
            if real_fabric_colorway_images_len > 0:
                for real_fabric_colorway_image in real_fabric_colorway_images:
                    color_way_image = get_image(
                        real_fabric_colorway_image, color_way_instance.name
                    )
                    get_photo_graphed_image = PhotographedImage.objects.filter(
                        color_way__fabric=fabric, color_way=color_way_instance
                    ).count()

                    if real_fabric_colorway_images_len >= get_photo_graphed_image:
                        photo_graphed_image, created = (
                            PhotographedImage.objects.get_or_create(
                                color_way=color_way_instance, image=color_way_image
                            )
                        )

        washing_id = Washing.objects.filter(
            id=laundry_informations["washingMethod"]
        ).last()
        dry_cleaning_id = DryCleaning.objects.filter(
            id=laundry_informations["dryCleaningMethod"]
        ).last()
        wring_id = Wring.objects.filter(id=laundry_informations["wringMethod"]).last()
        bleach_id = Bleach.objects.filter(
            id=laundry_informations["bleachMethod"]
        ).last()
        ironing_id = Ironing.objects.filter(
            id=laundry_informations["ironingMethod"]
        ).last()
        drying_id = Drying.objects.filter(
            id=laundry_informations["dryingMethod"]
        ).last()

        laundry, created = Laundry.objects.get_or_create(
            fabric=fabric,
            washing=washing_id,
            dry_cleaning=dry_cleaning_id,
            wring=wring_id,
            bleach=bleach_id,
            ironing=ironing_id,
            drying=drying_id,
        )

        specification, created = Specification.objects.get_or_create(
            fabric=fabric,
            thickness=specification["thickness"],
            weight=specification["weight"],
            transparency_level=specification["transparencyLevel"],
        )

        for composition in compositions:
            comp, created = Composition.objects.get_or_create(
                fabric=fabric,
                material=composition["material"],
                ratio=composition["ratio"],
            )

    return fabric


def get_image(thumbnail_url, name):
    # Step 1: Download the image from the URL
    response = requests.get(thumbnail_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Step 2: Open the image using Pillow
        img = Image.open(BytesIO(response.content))

        # Step 3: Convert the image to RGB mode (this ensures compatibility with .jpg)
        if img.mode in ("RGBA", "LA"):
            img = img.convert("RGB")

        # Step 4: Choose a format (png or jpg)
        format = "JPEG" if img.mode == "RGB" else "PNG"
        extension = "jpg" if format == "JPEG" else "png"

        # Step 5: Create a file-like object for the converted image
        file_name = f"{name.replace(' ', '_')}.{extension}"
        image_io = BytesIO()
        img.save(image_io, format=format)
        image_file = ContentFile(image_io.getvalue(), name=file_name)

        # Step 6: Create the ColorWay instance and save the image to the thumbnail field
        return image_file
    else:
        raise Exception(
            f"Failed to download image from {thumbnail_url}. Status code: {response.status_code}"
        )
