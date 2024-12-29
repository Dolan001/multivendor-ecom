from rest_framework import serializers

from product.models import Product
from product.serializers.category_serializers import CategorySerializer, SubCategorySerializer


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['total_likes', 'rating', 'total_sold']


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['total_likes', 'rating', 'total_sold']