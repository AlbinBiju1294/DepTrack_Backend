from django.shortcuts import render
from rest_framework.generics import ListAPIView
from .serializers import *
from rest_framework.permissions import AllowAny,IsAuthenticated
# Create your views here.


#view to list all Delivery Units
class GetAllDeliveryUnits(ListAPIView):
    """ Endpoint to list all available departments for logged in users  """

    permission_classes=(IsAuthenticated,)
    serializer_class= DeliveryUnitSerializer
    queryset= DeliveryUnit.objects.all()


