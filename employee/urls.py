#deptrack/employee/urls.py

from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('list/', ListOrCreateEmployeesView.as_view(), name='list-employees'),
]