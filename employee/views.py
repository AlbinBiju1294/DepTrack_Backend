from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Employee
from user.rbac import *
from .serializers import EmployeeSerializer

#To get the names of all employees
class ListOrCreateEmployeesView(ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsDuhead | IsAdmin | IsPm | IsHrbp)
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
