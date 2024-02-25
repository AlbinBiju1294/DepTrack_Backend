from rest_framework import serializers
from .models import Transfer,TransferDetails
from employee.models import Employee
from employee.serializers import EmployeeSerializer, EmployeeNestedSerializer

class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = "__all__"

class TransferDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferDetails
        fields = "__all__"


class TransferAndDetailsSerializer(serializers.ModelSerializer):
    details = TransferDetailsSerializer(many = False)
    employee = serializers.SerializerMethodField()

    class Meta:
        model = Transfer
        fields = '__all__'

    def get_employee(self, obj):
        try:
            if obj.employee_id:
                employee = Employee.objects.get(id=obj.employee_id.id)
                employee_serializer = EmployeeSerializer(employee)
                return employee_serializer.data
            return None
        except Exception as ex:
            return None

class TransferAndEmployeeSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()

    class Meta:
        model = Transfer
        fields = ["id","employee", "currentdu_id", "targetdu_id", "status", "transfer_date"]

    def get_employee(self, obj):
        try:
            if obj.employee:
                employee_serializer = EmployeeNestedSerializer(obj.employee)
                return employee_serializer.data
            return None
        
        except Exception as ex:
            return None
        
class TransferAndEmployeeSerializerTwo(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()

    class Meta:
        model = Transfer
        fields = ["id", "employee" , "currentdu_id", "targetdu_id", "status", "transfer_date"]

    def get_employee(self, obj):
        try:
            if obj.employee_id:
                employee = Employee.objects.get(id=obj.employee_id.id)
                employee_serializer = EmployeeNestedSerializer(employee)
                return employee_serializer.data
            return None
        except Exception as ex:
            return None
        

