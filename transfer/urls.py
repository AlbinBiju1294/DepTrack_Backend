from django.urls import path,include
from .views import *


urlpatterns = [
    path('create-transfer/', CreateTransferAPIView.as_view(), name='create-transfer'),
    path('get-transfer-details/', GetTransferDetailsAPIView.as_view(), name='get-transfer-details'),
    path('filter-transfers/', FilterTransfersAPIView.as_view(), name='filter-transfers'),
    path('track-initiated-requests/', GetInitiatedRequestsApiView.as_view(), name='track-initiated-request')
]