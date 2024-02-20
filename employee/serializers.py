from rest_framework import serializers
from .models import Employee

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'