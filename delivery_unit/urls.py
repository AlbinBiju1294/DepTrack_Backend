from django.urls import path, include
from .views import *

urlpatterns = [
    path("list-delivery-units/", GetAllDeliveryUnits.as_view(), name="listdus"),
    path("list-du-head/", GetDUNameAndHead.as_view(), name="listdus"),
    path('add-du', DeliveryUnitCreateAPIView.as_view(),
         name='create-deliveryunit'),
    path('dashboard-du-details', DashboardDuDetails.as_view(),
         name='dashboard-du-details'),
]
