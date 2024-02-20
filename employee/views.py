from django.shortcuts import render
from .serializers import *
from rest_framework.generics import ListAPIView
from rest_framework import generics, status, permissions
from user.rbac import *
from employee.models import Employee



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