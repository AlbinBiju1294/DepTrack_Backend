from django.shortcuts import render
from .models import Employee
from .serializers import EmployeeSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListCreateAPIView
from rest_framework import generics, status, permissions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from .serializers import *
from rest_framework.generics import ListAPIView
from rest_framework import generics, status, permissions
from user.rbac import *
from employee.models import Employee

# for pm listing
from rest_framework.response import Response
from user.models import User
from user.rbac import IsDuhead,IsAdmin
from .serializers import PmSerializer


# To list or create employee
class EmployeeListCreateView(ListCreateAPIView):
    """Allows the admin to list all the employees in the order of their
      employee_id.Details corresponding to all the fields of employee table
      is displayed.pagination is also applied"""
    permission_classes = (IsAdmin,)
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer

    pagination_class = LimitOffsetPagination

    def list(self, request, *args, **kwargs):

        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)

            if page is not None:

                serializer = self.get_serializer(page, many=True)
                res_data = {
                    'count': self.paginator.count,
                    'next': self.paginator.get_next_link(),
                    'previous': self.paginator.get_previous_link(),
                    'results': serializer.data
                }
                return Response(res_data, status=status.HTTP_200_OK)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response("Something went wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# To GET the list of Bands
class BandListView(ListCreateAPIView):
    """Extract the band levels from the band_level list so that the
      required band level can be selected by the DU or PM while filling form"""
    permission_classes=[IsDuhead|IsPm]
    def get(self, request):
        band_level = [("A1", "LEVEL1"), ("A2", "LEVEL2"),
                      ("B1", "LEVEL3"), ("B2", "LEVEL4"), ("C1", "LEVEL5")]
        band_levels = [band[0] for band in band_level]  
        return Response({"message": "Band levels retrieved successfully", "band_levels": band_levels}, status=status.HTTP_200_OK)    
    def post(self, request):
        return Response({"message":"Method \"POST\" not allowed."},status=status.HTTP_405_METHOD_NOT_ALLOWED)


# To list the new PM names in the C-DU
class PMListView(generics.ListAPIView):
    """Lists the names and id of the PMs in the du so that the du head can select one Pm 
      from this list for assigning to the new employee once the incoming transfer request 
      is accepted.User objects are filtered for the condition user_role=2"""
    serializer_class = PmSerializer
    permission_classes = [IsDuhead]
    pagination_class=None
    def get(self,request):
        try:
            logged_in_duhead_du = self.request.user.employee_id.du
            pm_users = User.objects.filter(user_role=2, employee_id__du=logged_in_duhead_du)
            if not pm_users: 
                return Response({"message": "No Project Managers available "}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(pm_users, many=True)
            return Response({ "message":"PM listing successful","data":serializer.data}, status=status.HTTP_200_OK)

        except Exception as ex:
            print(ex)
            return Response({"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# View to search employee table
class EmployeeSearchListView(generics.ListAPIView):
    """
    Lists employess according to name or part of name in the search field and department of the logged in DU head
    """
    serializer_class = EmployeeSerializer
    permission_classes = [IsDuhead,]

    def get_queryset(self):

        logged_in_user_department_id = self.request.user.employee_id.du.id
        name = self.request.data.get('name')
        queryset = Employee.objects.filter(du_id=logged_in_user_department_id)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

class DuHeadList(ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = DeliveryUnitMapping.objects.filter()
    serializer_class = DuAndEmployeeSerializer