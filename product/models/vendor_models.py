import uuid

from authentications.models import User
from core.models import BaseModel, CompressedImageField
from django.db import models
from utils.helper.helper_functions import content_file_path


class Category(BaseModel):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(upload_to=content_file_path, null=True, blank=True)

    def __str__(self):
        return f"{self.id}-{self.title}"


class SubCategory(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='sub_categories', null=True)
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(upload_to=content_file_path, null=True, blank=True)

    def __str__(self):
        return f"{self.id}-{self.title}"


class Vendor(BaseModel):
    vendor_id = models.UUIDField(unique=True, null=True, default=uuid.uuid4())
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_user')
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=50)
    address = models.TextField(null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user}-{self.name}'


class Product(BaseModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField(default=0.0)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='product_category')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, related_name='product_sub_category')
    image = CompressedImageField(blank=True, null=True, width=1920)
    total_likes = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    total_sold = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.id}-{self.name}'