from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from .serializers import *
from rest_framework.permissions import AllowAny,IsAuthenticated
from user.rbac import IsAdmin
from user.models import User
from employee.models import Employee
from employee.serializers import EmployeeSerializer
from rest_framework.response import Response

# Create your views here.


#view to list all Delivery Units
class GetAllDeliveryUnits(ListAPIView):
    """ Endpoint to list all available departments for logged in users  """

    permission_classes=(IsAuthenticated,)
    serializer_class= DeliveryUnitSerializer
    queryset= DeliveryUnit.objects.all()


class GetDUNameAndHead(ListAPIView):

    def get(self, request):
        permission_classes = [IsAdmin]

        du_heads = User.objects.filter(user_role=1).values_list('employee_id', flat=True)
        du_details = []
        for du_head_id in du_heads:
            du_head_emp = Employee.objects.get(id=du_head_id)
            du_head_name = du_head_emp.name
            du_name = du_head_emp.du_id.du_name
            du_details.append({
                'du_head_name': du_head_name,
                'du_name': du_name
            })

        return Response({du_details})
    





    

     

