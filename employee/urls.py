from django.urls import path,include
from .views import *


urlpatterns = [
    path('employee-list/', EmployeeListCreateView.as_view(), name='token_obtain_pair'),
    # path('employee-sort/', EmployeeSortView.as_view(), name='token_obtain_pair')
    path('bands', BandListView.as_view(), name='band-list'),
    path('pm-list', PMListView.as_view(), name='pm-list'),
    path("search-employee", EmployeeSearchListView.as_view(), name="searchemployee"),
    path("list-duheads", DuHeadList.as_view(), name="duheadlist"),
]
