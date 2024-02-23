from django.urls import path,include
from .views import *



urlpatterns = [
    path("list-delivery-units/", GetAllDeliveryUnits.as_view(), name="listdus"),
    path("list-du-head/", GetDUNameAndHead.as_view(), name="listdus"),
]
