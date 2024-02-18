from rest_framework import serializers
from .models import DeliveryUnit

class DeliveryUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryUnit
        fields = "__all__"