from django.urls import path,include
from .views import *


urlpatterns = [
    path('create-transfer/', CreateTransferAPIView.as_view(), name='create-transfer'),
    path('get-transfer-details/', GetTransferDetailsAPIView.as_view(), name='get-transfer-details'),
    path('filter-transfers/', FilterTransfersAPIView.as_view(), name='filter-transfers'),
    path('track-initiated-requests/', GetInitiatedRequestsApiView.as_view(), name='track-initiated-request'),
    path('individual-approval/', ChangeApprovalDatePmAPIView.as_view(), name='individual-approval'),
    path('list-transfer-history/', ListTransferHistoryAPIView.as_view(), name='list-transfer-history'),
    path('pending-approvals/', PendingApprovalsView.as_view(), name='pending-approvals'),
    path('bargraph-data/', NoOfTransfersInDUsAPIView.as_view(), name='bargraph-data'),
    path('cancel/', CancelTransfer.as_view(), name='cancel_transfer'),
    path('status-count/', TransferStatusCountAPIView.as_view(), name='transfer-status-count'),
    path("request-rejected", TargetDURejectAPIView.as_view(), name="request-rejected")
]