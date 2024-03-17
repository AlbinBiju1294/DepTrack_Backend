from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from .serializers import *
from rest_framework.permissions import AllowAny,IsAuthenticated
from user.rbac import *
from user.models import User
from employee.models import *
from employee.serializers import EmployeeSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import DeliveryUnit
from .serializers import DuSerializer
from user.rbac import IsAdmin
import logging

logger = logging.getLogger("django")

# To add new Du
class DeliveryUnitCreateAPIView(APIView):
    """Allows the admin to add new Du to the delivery_unit table and map du head and hrbp for the same.
       The Du_name is given in the body.If the entered Du already exists
       then an error message will be displayed"""
   
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            du_name = request.data.get('du_name')
            du_head_id=request.data.get('du_head_id')
            hrbp_id=request.data.get('hrbp_id')
            if not (du_name and du_head_id and hrbp_id):
                return Response({"message": "du_name,du_head_id and hrbp_id is required in the request body"}, status=status.HTTP_400_BAD_REQUEST)
            if DeliveryUnit.objects.filter(du_name=du_name).exists():
                return Response({"message": "Delivery Unit with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)

            du_instance=DeliveryUnit.objects.create(du_name=du_name)
            du_head_instance=Employee.objects.get(id=du_head_id)
            du_head_instance.du_id=du_instance
            du_head_instance.save()
            hrbp_instance=Employee.objects.get(id=hrbp_id)
            hrbp_instance.du_id=du_instance
            hrbp_instance.save()
            du_mapping_instance =  DeliveryUnitMapping.objects.create(
                    du_id=du_instance,
                    du_head_id=du_head_instance,
                    hrbp_id=hrbp_instance
            )
            if du_instance and du_mapping_instance:
                return Response({"message": "New DU and DuMapping added successfully"}, status=status.HTTP_201_CREATED)
            else:
                # If one of the instances failed to create
                return Response({"message": "Failed to create one or more instances"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response( {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                return Response({"data": serializer.data, "message": "Departments Listed"}, status=status.HTTP_200_OK)
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
    permission_classes = [IsAdmin | IsDuhead | IsPm | IsHrbp]

    def get(self, request):
        try:
            logged_in_user_du_id = self.request.user.employee_id.du_id.id
            du_name = DeliveryUnit.objects.get(id=logged_in_user_du_id).du_name
            pms_in_du_count = Employee.objects.filter(du_id=logged_in_user_du_id, user__user_role=2).count()
            total_no_of_employees = Employee.objects.filter(du_id=logged_in_user_du_id).count()

            result = {'du_name': du_name,
                    'no_of_pms': pms_in_du_count,
                    'no_of_employees': total_no_of_employees}
            
            if result:
                return Response({'data': result, 'message': 'Du details retreived successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Du details couldnot be retreived.'}, status=status.HTTP_404_NOT_FOUND)

        
        except Exception as e:
                logger.error(e)
                return Response({'error': {str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    





    

     

