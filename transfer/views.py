# views.py
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime
from rest_framework.views import APIView
from .serializers import TransferSerializer, TransferDetailsSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Transfer, TransferDetails
from employee.models import Employee
from .serializers import TransferSerializer, TransferDetailsSerializer, TransferAndDetailsSerializer, TransferAndEmployeeSerializer
from user.rbac import IsDuhead, IsPm, IsHrbp


# saves the transfers initiated into the transfers and transfer details table
class CreateTransferAPIView(APIView):
    permission_classes = [IsPm | IsDuhead]
    """The data is serialized using transfer serializer. If it is valid it is saved 
    into the transfer table. The transfer_id from the transfer instance is added 
    to the request data and then it is added to transfer details table along with
    other details"""

    def post(self, request):
        try:
            transfer_serializer = TransferSerializer(data=request.data)
            if transfer_serializer.is_valid():
                transfer = transfer_serializer.save()
                request.data['transfer'] = transfer.id
                transfer_detail_serializer = TransferDetailsSerializer(
                    data=request.data)
                if transfer_detail_serializer.is_valid():
                    transfer_detail_serializer.save()
                    return Response({"status": True, 'message': 'Transfer created successfully.'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"status": True, 'message': transfer_detail_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(transfer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"status": False, "message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# view to get the whole details of the transfer by passing transfer id
class GetTransferDetailsAPIView(APIView):
    permission_classes = [IsPm | IsDuhead]
    """transfer id is extracted from the request body. Then the transfer instance is 
    obtained using the transfer id. Then the transfer details along with employee details
    is returned"""

    def get(self, request):
        try:
            transfer_id = request.data.get('transfer_id')
            transfer = Transfer.objects.get(id=transfer_id)
            if transfer:
                serializer = TransferAndDetailsSerializer(transfer)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"status": False, "message": "Transfer details not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': False, "message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# filters the transfers based on the given query parameters
class FilterTransfersAPIView(APIView):
    permission_classes = [IsPm | IsDuhead | IsHrbp]
    """Query params are taken into a variable filter_params and based on those parameters 
    details are fetched from transfer table and the filtered content is returned as
    response"""

    def get(self, request):
        try:
            filter_params = request.query_params
            query_set = Transfer.objects.all()
            for key, value in filter_params.items():
                if key == 'employee_name':
                    query_set = query_set.filter(
                        employee__name__icontains=value)
                elif value and key != 'start_date' and key != 'end_date':
                    query_set = query_set.filter(**{key: value})

            if 'start_date' in filter_params and 'end_date' in filter_params:
                start_date = datetime.strptime(
                    filter_params['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(
                    filter_params['end_date'], '%Y-%m-%d').date()
                query_set = query_set.filter(
                    transfer_date__range=(start_date, end_date))

            if query_set:
                serializer = TransferAndDetailsSerializer(query_set, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"status": False, "message": "Transfers not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': False, "message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# to track the initiated transfer requests.
class GetInitiatedRequestsApiView(APIView):
    permission_classes = [IsDuhead]
    """transfer details are fetched where the du_id is same as that of the requestor
    and the status is either 1 or 2 which indicates initiated by PM or pending 
    approval"""

    def get(self, request):
        try:
            du_id = request.data.get('du_id')
            query_set = Transfer.objects.filter(
                Q(currentdu=du_id) & (Q(status=1) | Q(status=2)))
            print(query_set)
            if query_set:
                serializer = TransferAndEmployeeSerializer(query_set, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"status": False, "message": "Transfer details not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': False, "message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#To post the details when a request is approved by T-DU head
class ChangeApprovalDatePmAPIView(APIView):
    """
    When a target DU head views the detailed view of a transfer request, they can approve or reject it.
    If 'approve' is clicked then the transfer date can be changed and a new pm can be assigned. This data 
    is posted into the transfer table.
    """

    permission_classes = [IsDuhead]
    
    def put(self, request):
        try:
            data = request.data
            transfer_id = data.get("id")
            transfer = Transfer.objects.get(id=transfer_id)
            new_pm = data.get("new_pm")
            assigned_emp_pm =  Employee.objects.get(id=new_pm)
            transfer.transfer_date = data.get("transfer_date")
            transfer.new_pm = assigned_emp_pm
            transfer.status = 3
            print(assigned_emp_pm)
            transfer.save()
            return Response({"status": True, 'message': 'Transfer date and pm changed successfully.'}, status=status.HTTP_201_CREATED)            

        except Exception as e:
            print(e)
            return Response({"status": False, "message": f"Something went wrong. {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

# To list all the transfers that happened in a DU, in all statuses 
class ListTransferHistoryAPIView(APIView):
    """
    Lists all the transfers that happened in a DU, both incoming and outgoing transfers. It takes details 
    from both the transfer table and employee table.
    """
    permission_classes = [IsAuthenticated, IsDuhead | IsPm | IsHrbp]

    def get(self, request):
        try:
            employee_id = request.user.employee_id.id
            authenticated_employee = Employee.objects.get(id=employee_id)
            du_id = authenticated_employee.du.id                                             #department of DU head
            transfer = Transfer.objects.filter(Q(currentdu=du_id) | Q(targetdu=du_id))       #data from transfer table
            serializer = TransferAndEmployeeSerializer(transfer, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # logger.error(f"Transfer History Listing API: {e}")
            return Response({"status": False, "message": f"Something went wrong. {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#To display all the pending approvals for a DU head.
class PendingApprovalsView(APIView):
    """
    To view all the pending transfer approval requests for a DU head both internal and external i.e., the requests
    initiated by PM which awaits the approval of DU head and the requests from another DU to accept an employee from
    their respective DU. 
    """
    permission_classes = [IsAuthenticated, IsDuhead]

    def get(self, request):
        try:
            employee_id = request.user.employee_id.id
            authenticated_employee = Employee.objects.get(id=employee_id)
            du_id = authenticated_employee.du.id
            if request.data.get('tab_switch_btn') == 1:                                       
                transfer_requests = Transfer.objects.filter(status=2, targetdu=du_id)
            elif request.data.get('tab_switch_btn') == 2:
                transfer_requests = Transfer.objects.filter(status=1, currentdu=du_id)
            serializer = TransferAndEmployeeSerializer(transfer_requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"status": False, "message": f"Something went wrong. {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)