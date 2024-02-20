from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import filters
from rest_framework.response import Response

from .models import Employee
from user.rbac import *
from .serializers import EmployeeSerializer, EmployeeNameIdListSerializer

#To get the names of all employees
class ListOrCreateEmployeesView(ListCreateAPIView):

    permission_classes = (IsAuthenticated, IsDuhead | IsAdmin | IsPm | IsHrbp)

    def get(self, request):
      
            accessorId = request.user.id
            userEmployee = Employee.objects.get(id=accessorId)
            du_id = userEmployee.du.id
            search_query = request.query_params.get('search', '')  # Get search query parameter
            employeesInDu = Employee.objects.filter(du=du_id, name__icontains=search_query)
            serializer = EmployeeNameIdListSerializer(employeesInDu, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


            
