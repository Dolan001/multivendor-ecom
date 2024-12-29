import base64
import os
import random
from datetime import datetime
from io import BytesIO

from django.core.cache import cache
from django.core.files import File
from django.core.validators import RegexValidator
from django.utils.text import slugify
from PIL import Image, ImageOps

# phone number validate
phone_validator = RegexValidator(
    r"^(\+?\d{0,4})?\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{4}\)?)?$",
    "The phone number provided is invalid",
)


def content_file_path(instance, filename):
    model_name = instance.__class__.__name__.replace("Model", "")
    ext = filename.split(".")[-1]
    current_date = datetime.now()
    date_path = current_date.strftime("%Y-%m-%d")
    unique_filename = f"{instance}-{instance.pk}.{ext}"
    return os.path.join(model_name, date_path, unique_filename)


def replace_special_characters(text):
    # A list of special_characters to be removed
    special_characters = ["@", "#", "$", "*", "&", "."]
    normal_string = text
    for i in special_characters:
        # Replace the special character with an empty string
        normal_string = normal_string.replace(i, "")
    return normal_string


def unique_slugify(instance, title, iteration=1):
    """
    Generates a unique slug for the given model instance.
    """
    plain_text = replace_special_characters(title)
    slug = slugify(plain_text)
    if slug == "":
        slug = f"{instance.__class__.__name__}-{random.randint(1, 10)}"
    if instance.slug == slug:
        return slug
    if iteration > 1:
        slug += f"{'-' if len(slug) else instance.pk}{iteration}"
    try:
        queryset = instance.__class__.everything.filter(slug=slug)
    except:
        queryset = instance.__class__.objects.filter(slug=slug)
    if queryset.exists():
        iteration += 1
        return unique_slugify(instance, title, iteration=iteration)
    return slug


def compress_image(file, q, h, w):
    """
    Image size compression
    """
    try:
        im = Image.open(file)
        image = im.convert("RGB")
        image = ImageOps.exif_transpose(image)
        im_io = BytesIO()
        image.save(im_io, im.format, quality=q, width=w, height=h, optimize=True)

        return File(im_io, name=file.name)
    except IOError:
        return file


def resize_image(file, height, width):
    img = Image.open(file)

    img_format = img.format

    # Resize the image
    img = img.resize((height, width), Image.Resampling.LANCZOS)

    # Convert to RGB if saving as JPEG
    if img_format == "PNG":
        if img.mode in ("RGBA", "LA"):
            # If it has an alpha channel, keep the alpha for PNG
            img = img.convert("RGBA")
    else:
        # Convert to RGB if not PNG
        if img.mode in ("RGBA", "LA"):
            img = img.convert("RGB")

    # Save the resized image to a BytesIO object
    img_io = BytesIO()
    img.save(img_io, format=img_format)

    return img_io


def calculate_rating(reviews):
    total_rating = 0
    if reviews:
        for review in reviews:
            total_rating += review.rating

        if total_rating > 0:
            avg_rating = total_rating / len(reviews)
        else:
            avg_rating = 0
    else:
        avg_rating = total_rating
    return round(avg_rating, 1)


def string_to_base64(input_string):
    return base64.b64encode(input_string.encode()).decode()


def base64_to_string(input_base64):
    return base64.b64decode(input_base64).decode()


def calculate_discount(discount, obj):
    if discount:
        if discount.discount_type == "PERCENTAGE":
            discounted_price = obj.price - ((discount.amount / 100) * obj.price)
        else:
            discounted_price = obj.price - discount.amount
        data = {
            "type": discount.discount_type,
            "discounted_price": discounted_price,
            "amount": discount.amount,
        }
    else:
        data = {"type": None, "discounted_price": obj.price, "amount": 0}

    return data


def cache_object(*, key, obj, timeout=60 * 60):
    # Store the object in Redis
    cache.set(key, obj, timeout)


def get_cached_object(key):
    # Retrieve the cached object from Redis
    return cache.get(key)


def delete_cached_object(key):
    # Delete the cached object from Redis
    cache.delete(key)
