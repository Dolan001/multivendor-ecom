from rest_framework import serializers
from product.models import Vendor


class VendorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendor
        fields = '__all__'
        read_only_fields = ['vendor_id']
