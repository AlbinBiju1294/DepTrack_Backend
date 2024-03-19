from rest_framework import serializers
from .models import *
from user.models import User
from delivery_unit.models import DeliveryUnit
from delivery_unit.serializers import DeliveryUnitSerializer,NestedDeliveryUnitSerializer


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class PmSerializer(serializers.ModelSerializer):
    employee_details = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["employee_details"]
        
    def get_employee_details(self, obj):
        try:
            if obj.employee_id:
                employee = Employee.objects.get(id=obj.employee_id.id)
                employee_serializer = EmployeeNestedSerializer(employee)
                return employee_serializer.data
            return None
        except Exception as ex:
            return None


class EmployeeNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id","employee_number", "name","designation","mail_id"]

class DeliveryUnitMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryUnitMapping
        fields = '__all__'


class DuAndEmployeeSerializer(serializers.ModelSerializer):
    du_head = serializers.SerializerMethodField(source='du_head_id')
    du = serializers.SerializerMethodField(source='du_id')
    

    class Meta:
        model = DeliveryUnitMapping
        fields = ['id','du','du_head','hrbp_id']

    def get_du_head(self, obj):
        try:
            if obj.du_head_id_id:
                employee = Employee.objects.get(id=obj.du_head_id.id)
                employee_serializer = EmployeeNestedSerializer(employee)
                return employee_serializer.data
            return None
        except Exception as ex:
            return None
        
    def get_du(self, obj):
        try:
            if obj.du_id:
                du = DeliveryUnit.objects.get(id=obj.du_id.id)
                du_serializer = NestedDeliveryUnitSerializer(du)
                return du_serializer.data
            return None
        except Exception as ex:
            return None