from django.urls import path,include
from .views import *


urlpatterns = [
    path('employee-list/', EmployeeListCreateView.as_view(), name='token_obtain_pair'),
    path('bands/', BandListView.as_view(), name='band-list'),
    path('pm-list/', PMListView.as_view(), name='pm-list'),
    path("search-employee/", EmployeeSearchListView.as_view(), name="searchemployee"),
    path("list-duheads/", DuHeadAndDuList.as_view(), name="duheadlist"),
    path("update-duhead/", UpdateDUHeadAPIView.as_view(), name="update-duhead"),
    path("upload-xl", EmployeeUpdate.as_view(), name="upload-xl"),
    path("get-du-employees/", NoOfEmployeesInDUsAPIView.as_view(), name="get-du-employees"),
    path("get-du-candidates/", PotentialDuHeads.as_view(), name="get-du-candidates"),
    path("get-hrbp-candidates/", PotentialHrbps.as_view(), name="get-hrbp-candidates")
]
