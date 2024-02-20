from django.urls import path,include
from .views import *



urlpatterns = [
    path("list-delivery-units/", GetAllDeliveryUnits.as_view(), name="listdus"),
]
