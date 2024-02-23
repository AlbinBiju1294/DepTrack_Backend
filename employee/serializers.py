from rest_framework import serializers
from .models import *
from user.models import User


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class PmSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','id']


class EmployeeNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["employee_number", "name"]

class DeliveryUnitMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryUnitMapping
        fields = '__all__'



        