from rest_framework import serializers

from order.models import Order, OrderProduct, Cart, CartProduct
from product.models import Product


class OrderProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderProduct
        fields = '__all__'
        read_only_fields = ['cart', 'is_active']


class OrderSerializer(serializers.ModelSerializer):
    cart_product_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    order_products = OrderProductSerializer(source='orders', read_only=True, many=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = [
            'customer',
            'is_active',
            'product_amount',
            'discount',
            'grand_total',
            'delivery_charge',
            'payment',
            'payment_key',
            'payment_type',
            'payment_response',
            'delivery_number',
            "order_products",
            "vendor"
        ]

    def create(self, validated_data):
        cart_product_ids = validated_data.pop("cart_product_ids", [])
        customer = self.context.get("request").user

        if len(cart_product_ids) <= 0:
            raise serializers.ValidationError(
                {"detail": "You must send minimum one cart product"}
            )

        product_carts = Cart.objects.filter(id__in=cart_product_ids, customer=customer)
        # if product_cart.customer != customer:
        #     raise serializers.ValidationError(
        #         {"detail": "You can not order others product"}
        #     )

        if not product_carts:
            raise serializers.ValidationError(
                {"detail": "No cart product found, please check your cart again"}
            )
        validated_data['customer'] = customer

        for product_cart in product_carts:
            product_cart_items = CartProduct.objects.filter(cart=product_cart)
            print(product_cart)

            order = Order.objects.create(vendor=product_cart.vendor, **validated_data)
            order.product_amount = product_cart.product_amount
            order.discount = product_cart.discount
            order.delivery_charge = product_cart.delivery_charge
            order.grand_total = product_cart.grand_total
            order.save()

            for product_cart_item in product_cart_items:
                print(product_cart_item)
                OrderProduct.objects.create(
                    order=order,
                    product=product_cart_item.product,
                    quantity=product_cart_item.quantity,
                )
            # product_cart.delete()
        return order
