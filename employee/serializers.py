from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"

class EmployeeNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["employee_number", "name"]