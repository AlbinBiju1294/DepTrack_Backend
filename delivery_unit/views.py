from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from .serializers import *
from rest_framework.permissions import AllowAny,IsAuthenticated
from user.rbac import *
from user.models import User
from employee.models import Employee
from employee.serializers import EmployeeSerializer
from rest_framework.response import Response
from rest_framework import status

# Create your views here.


#view to list all Delivery Units
class GetAllDeliveryUnits(ListAPIView):
    """ Endpoint to list all available departments for logged in users  """

    permission_classes=(IsAuthenticated,)
    serializer_class= DeliveryUnitSerializer
    queryset= DeliveryUnit.objects.all()


class GetDUNameAndHead(ListAPIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        

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
    
class DashboardDuDetails(APIView):
    permission_classes = [IsAdmin | IsDuhead | IsPm | IsPm]

    def get(self, request):
        try:
            logged_in_user_du_id = self.request.user.employee_id.du_id
            du_name = DeliveryUnit.objects.get(id=logged_in_user_du_id).du_name
            pms_in_du_count = Employee.objects.filter(du_id=logged_in_user_du_id, user__user_role=2).count()
            total_no_of_employees = Employee.objects.filter(du_id=logged_in_user_du_id).count()

            result = {'du_name': du_name,
                    'no_of_pms': pms_in_du_count,
                    'no_of_employees': total_no_of_employees}
            
            if result:
                return Response({'result': result, 'message': 'Du details retreived successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Du details couldnot be retreived.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        except Exception as e:
                return Response({'message': 'Du details couldnot be retreived.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    





    

     

