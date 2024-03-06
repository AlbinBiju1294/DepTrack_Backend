from rest_framework import serializers
from .models import Transfer,TransferDetails, RequestStatus
from employee.models import Employee
from employee.serializers import EmployeeSerializer, EmployeeNestedSerializer
from delivery_unit.models import DeliveryUnit
from delivery_unit.serializers import DuSerializer


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = "__all__"


class TransferDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferDetails
        fields = "__all__"


class TransferAndDetailsSerializer(serializers.ModelSerializer):
    details = TransferDetailsSerializer(many=False)
    employee = serializers.SerializerMethodField()
    currentdu = serializers.SerializerMethodField()
    initiated_by = serializers.SerializerMethodField()


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
    
    def get_currentdu(self, obj):
        try:
            if obj.currentdu_id:
                currentdu = DeliveryUnit.objects.get(id=obj.currentdu_id.id)
                currentdu_serializer = DuSerializer(currentdu)
                return currentdu_serializer.data
            return None
        except Exception as ex:
            return None
        
    def get_initiated_by(self, obj):
        try:
            if obj.initiated_by:
                initiated_by = Employee.objects.get(id=obj.initiated_by.id)
                employee_serializer = EmployeeNestedSerializer(initiated_by)
                return employee_serializer.data
            return None
        except Exception as ex:
            return None


class TransferAndEmployeeSerializer(serializers.ModelSerializer):
    employee = serializers.SerializerMethodField()
    currentdu = serializers.SerializerMethodField()
    targetdu = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    initiated_by = serializers.SerializerMethodField()

    class Meta:
        model = Transfer
        fields = ["id", "employee" , "currentdu", "targetdu", "status", "transfer_date", "initiated_by"]

    def get_employee(self, obj):
        try:
            if obj.employee_id:
                employee = Employee.objects.get(id=obj.employee_id.id)
                employee_serializer = EmployeeNestedSerializer(employee)
                return employee_serializer.data
            return None
        except Exception as ex:
            return None
    
    def get_currentdu(self, obj):
        try:
            if obj.currentdu_id:
                currentdu = DeliveryUnit.objects.get(id=obj.currentdu_id.id)
                currentdu_serializer = DuSerializer(currentdu)
                return currentdu_serializer.data
            return None
        except Exception as ex:
            return None
        
    def get_targetdu(self, obj):
        try:
            if obj.targetdu_id:
                targetdu = DeliveryUnit.objects.get(id=obj.targetdu_id.id)
                targetdu_serializer = DuSerializer(targetdu)
                return targetdu_serializer.data
            return None
        except Exception as ex:
            return None
        
    def get_status(self, obj):
        try:
            if obj.status:
                for code, status_string in RequestStatus.REQUEST_STATUS:
                    if code == obj.status:
                        return status_string
            return None
        except Exception as ex:
            return None
        
    def get_initiated_by(self, obj):
        try:
            if obj.initiated_by:
                initiated_by = Employee.objects.get(id=obj.initiated_by.id)
                employee_serializer = EmployeeNestedSerializer(initiated_by)
                return employee_serializer.data
            return None
        except Exception as ex:
            return None

