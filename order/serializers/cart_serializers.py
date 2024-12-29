from rest_framework import serializers

from order.models import Cart, CartProduct
from product.models import Product


class CartProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartProduct
        fields = '__all__'
        read_only_fields = ['cart', 'is_active']


class CartSerializer(serializers.ModelSerializer):
    carts = CartProductSerializer(many=True)

    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = ['customer', 'is_active', 'product_amount', 'discount', 'grand_total', 'delivery_charge']

    def create(self, validated_data):
        cart_products = validated_data.get("carts")
        vendor = validated_data.get("vendor")
        print(cart_products)
        customer = self.context.get("request").user

        cart, _ = Cart.objects.get_or_create(
            customer=customer, vendor=vendor
        )
        product_amount = cart.product_amount
        discount = cart.discount
        delivery_charge = cart.delivery_charge

        for cart_product in cart_products:
            print(cart_product)
            # product = Product.objects.filter(id=product)
            product = cart_product.get('product')
            quantity = cart_product.get('quantity')
            if int(quantity) == 0:
                quantity = 1
            cp, cp_created = CartProduct.objects.get_or_create(
                cart=cart, product=product
            )
            if cp_created:
                cp.quantity = quantity
                cp.save()
                product_amount += (product.price * quantity)
            else:
                cp.quantity += quantity
                cp.save()
                product_amount += (product.price * quantity)

        cart.product_amount = product_amount
        cart.discount = discount
        cart.delivery_charge = delivery_charge
        grand_total = (product_amount + delivery_charge) - discount
        cart.grand_total = grand_total
        cart.save()
        return cart
