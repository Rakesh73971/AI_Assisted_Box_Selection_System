from rest_framework import serializers
from .models import Product, Box, Order, OrderItem, ShipmentRecommendation

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'sku', 'width', 'height', 'depth', 'weight', 'volume')


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = ('id', 'name', 'width', 'height', 'depth', 'max_weight', 'cost', 'is_active', 'volume')


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    product = ProductSerializer(read_only=True)
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = OrderItem
        fields = ('id', 'product_id', 'product', 'quantity')

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product with this ID does not exist.")
        return value


class ShipmentRecommendationSerializer(serializers.ModelSerializer):
    selected_box = BoxSerializer(read_only=True)

    class Meta:
        model = ShipmentRecommendation
        fields = (
            "id",
            "selected_box",
            "volume_utilization",
            "weight_utilization",
            "cost",
            "packing_layout",
            "error_reason",
            "calculated_at",
        )


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    recommendation = ShipmentRecommendationSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'order_number', 'customer_name', 'status', 'created_at', 'items', 'recommendation')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            OrderItem.objects.create(order=order, product=product, quantity=item_data['quantity'])
        return order
