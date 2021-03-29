from rest_framework import serializers
from couriers.models import Courier, Order
from django.core.validators import MinValueValidator


class CouriersDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = ('courier_id', 'courier_type', 'regions', 'working_hours')


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('order_id', 'weight', 'region', 'delivery_hours')


class CourierOrderSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField(validators=[MinValueValidator(1)])
    order_id = serializers.IntegerField(validators=[MinValueValidator(1)])
    complete_time = serializers.DateTimeField()
