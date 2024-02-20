from rest_framework import serializers
from .models import Transfer,TransferDetails
from employee.models import Employee
from employee.serializers import EmployeeSerializer



class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = "__all__"

class TransferDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferDetails
        fields = "__all__"


class TransferAndDetailsSerializer(serializers.ModelSerializer):
    details = TransferDetailsSerializer(many=True)
    employee = serializers.SerializerMethodField()

    class Meta:
        model = Transfer
        fields = '__all__'

    def get_employee(self, obj):
        try:
            if obj.employee:
                employee = Employee.objects.get(id=obj.employee.id)
                employee_serializer = EmployeeSerializer(employee)
                return employee_serializer.data
            return None
        except Exception as ex:
            return None