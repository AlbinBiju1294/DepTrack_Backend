# urls.py
from django.urls import path
from .views import DeliveryUnitCreateAPIView

urlpatterns = [
    path('add-du', DeliveryUnitCreateAPIView.as_view(), name='create-deliveryunit'),
]
