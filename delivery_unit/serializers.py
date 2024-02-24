from rest_framework import serializers
from .models import DeliveryUnit

class DeliveryUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryUnit
        fields = "__all__"

class DuSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryUnit
        fields = ['du_name']
    
class NestedDeliveryUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryUnit
        fields = ["id","du_name"]