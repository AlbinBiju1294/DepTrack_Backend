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
from rest_framework.views import APIView
from .models import DeliveryUnit
from .serializers import DuSerializer
from user.rbac import IsAdmin

# To add new Du 
class DeliveryUnitCreateAPIView(APIView):
    """Allows the admin to add new Du to the delivery_unit table.
       The Du_name is given in the body.If the entered Du already exists 
       then an error message will be displayed"""
    
    permission_classes = [IsAdmin]
    def post(self, request):
        try:
            serializer = DuSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"new DU added successfully"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res_data = {"message": " Something went wrong !", "data": {"error": str(e)}, }
            return Response(res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#view to list all Delivery Units
class GetAllDeliveryUnits(ListAPIView):
    """ Endpoint to list all available departments for logged in users  """

    permission_classes=(IsAuthenticated,)
    serializer_class= DeliveryUnitSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = DeliveryUnit.objects.all()
            if  queryset.exists():
                serializer = self.get_serializer(queryset, many=True)
                return Response({"data": serializer.data, "Message": "Departments Listed"}, status=status.HTTP_200_OK)
            else:
                return  Response({"error": "Failed to retrieve Departments"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Internal Error","error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                return Response({'error': 'Du details couldnot be retreived.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        except Exception as e:
                return Response({'error': 'Du details couldnot be retreived.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    





    

     

