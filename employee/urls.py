from django.urls import path,include
from .views import *


urlpatterns = [
    path("search-employee", EmployeeSearchListView.as_view(), name="searchemployee"),
]
