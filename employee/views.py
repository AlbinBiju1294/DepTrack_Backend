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
from user.rbac import IsDuhead
from .serializers import PmSerializer




# To list or create employee
class EmployeeListCreateView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    queryset = Employee.objects.all().order_by('-id')
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
        


##To GET the list of Bands
class BandListView(ListCreateAPIView):
    def get(self, request):
        band_level = [("A1", "LEVEL1"), ("A2", "LEVEL2"),
                      ("B1", "LEVEL3"), ("B2", "LEVEL4"), ("C1", "LEVEL5")]
        band_levels = [band[0] for band in band_level]  # Extract the band levels from the band_level list
        return Response({"band_levels": band_levels})
    


##To list the new PM names in the C-DU
class PMListView(generics.ListAPIView):
    serializer_class = PmSerializer
    permission_classes = [IsDuhead]

    def get_queryset(self):
        try:
            logged_in_duhead_du = self.request.user.employee_id.du
            pm_users = User.objects.filter(user_role=2, employee_id__du=logged_in_duhead_du )
            return pm_users
        except Exception as ex:
            print(ex)
            return Response({"message":"Something wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
      






#View to search employee table 
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