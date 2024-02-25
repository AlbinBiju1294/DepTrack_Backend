# views.py
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime
from rest_framework.views import APIView
from .serializers import TransferSerializer, TransferDetailsSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Transfer
from employee.models import Employee
from .serializers import TransferSerializer, TransferDetailsSerializer, TransferAndDetailsSerializer, TransferAndEmployeeSerializer, TransferAndEmployeeSerializerTwo
from user.rbac import IsDuhead, IsPm, IsHrbp, IsAdmin
import logging

logger = logging.getLogger("django")


# saves the transfers initiated into the transfers and transfer details table
class CreateTransferAPIView(APIView):
    permission_classes = [IsPm | IsDuhead]
    """The data is serialized using transfer serializer. If it is valid it is saved 
    into the transfer table. The transfer_id from the transfer instance is added 
    to the request data and then it is added to transfer details table along with
    other details"""

    def post(self, request):
        try:
            current_du_id = request.data.get('currentdu_id')
            target_du_id = request.data.get('targetdu_id')
            employee_id = request.data.get('employee_id')

            if current_du_id == target_du_id and current_du_id != None and target_du_id != None:
                return Response({'error': 'Current and target DU cannot be the same.'}, status=status.HTTP_400_BAD_REQUEST)

            existing_transfer = Transfer.objects.filter(
                employee_id=employee_id).exclude(status__in=[3, 4, 5]).first()
            if existing_transfer:
                return Response({'error': 'Employee transfer already in progress.'}, status=status.HTTP_400_BAD_REQUEST)
            transfer_serializer = TransferSerializer(data=request.data)
            if transfer_serializer.is_valid():
                transfer = transfer_serializer.save()
                request.data['transfer_id'] = transfer.id
                transfer_detail_serializer = TransferDetailsSerializer(
                    data=request.data)
                if transfer_detail_serializer.is_valid():
                    transfer_detail_serializer.save()
                    return Response({'message': 'Transfer created successfully.'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': transfer_detail_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": transfer_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# view to get the whole details of the transfer by passing transfer id
class GetTransferDetailsAPIView(APIView):
    permission_classes = [IsPm | IsDuhead]
    """transfer id is extracted from the request body. Then the transfer instance is 
    obtained using the transfer id. Then the transfer details along with employee details
    is returned"""

    def get(self, request):
        try:
            transfer_id = request.data.get('transfer_id')
            if (transfer_id == ''):
                return Response({"error": "transfer id shouldn't be null"},status=status.HTTP_400_BAD_REQUEST)
            transfer = Transfer.objects.get(id=transfer_id)
            if transfer:
                serializer = TransferAndDetailsSerializer(transfer)
                return Response({"data": serializer.data, "message": "Transfer details retreived"}, status=status.HTTP_200_OK)
            return Response({"error": "Transfer details not found"}, status=status.HTTP_404_NOT_FOUND)
        except Transfer.DoesNotExist:
            return Response({"error": f"Transfer details with id {transfer_id} not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.critical(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# filters the transfers based on the given query parameters
class FilterTransfersAPIView(APIView):
    permission_classes = [IsPm | IsDuhead | IsHrbp | IsAdmin]
    """Query params are taken into a variable filter_params and based on those parameters 
    details are fetched from transfer table and the filtered content is returned as
    response"""

    def get(self, request):
        try:
            filter_params = request.data
            query_set = Transfer.objects.all()
            for key, value in filter_params.items():
                if key == 'employee_name':
                    query_set = query_set.filter(
                        employee_id__name__icontains=value)
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
                serializer = TransferAndEmployeeSerializerTwo(
                    query_set, many=True)
                return Response({"data": serializer.data, "message": "filtered successfully"}, status=status.HTTP_200_OK)
            return Response({"error": "Transfers not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# to track the initiated transfer requests.
class GetInitiatedRequestsApiView(APIView):
    """transfer details are fetched where the du_id is same as that of the requestor
    and the status is either 1 or 2 which indicates initiated by PM or pending 
    approval"""

    permission_classes = [IsDuhead | IsAdmin]

    def get(self, request):
        try:
            du_id = request.data.get('du_id')
            query_set = Transfer.objects.filter(
                Q(currentdu_id=du_id) & (Q(status=1) | Q(status=2)))
            logger.info(query_set)
            if query_set:
                serializer = TransferAndEmployeeSerializerTwo(
                    query_set, many=True)
                return Response({"data": serializer.data,"message":"Initiated requests retreived successfully"}, status=status.HTTP_200_OK)
            return Response({"message": "Transfer details not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# To post the details when a request is approved by T-DU head
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
            new_pm = data.get("newpm_id")
            assigned_emp_pm = Employee.objects.get(id=new_pm)
            transfer.transfer_date = data.get("transfer_date")
            transfer.newpm_id = assigned_emp_pm
            transfer.status = 3
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
            du_id = authenticated_employee.du.id  # department of DU head
            transfer = Transfer.objects.filter(Q(currentdu=du_id) | Q(
                targetdu=du_id))  # data from transfer table
            serializer = TransferAndEmployeeSerializer(transfer, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # logger.error(f"Transfer History Listing API: {e}")
            return Response({"status": False, "message": f"Something went wrong. {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# To display all the pending approvals for a DU head.
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
                transfer_requests = Transfer.objects.filter(
                    status=2, targetdu=du_id)
            elif request.data.get('tab_switch_btn') == 2:
                transfer_requests = Transfer.objects.filter(
                    status=1, currentdu=du_id)
            serializer = TransferAndEmployeeSerializer(
                transfer_requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": False, "message": f"Something went wrong. {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# To cancel the initiated transfer request by the duhead
class CancelTransfer(APIView):
    permission_classes = [IsDuhead]
    """The transfer status of a particular tarnsfer_id is changed to 
        the new status=5 in the transfer table which indicates that the 
        transfer is cancelled.Done bythe current_du head"""

    def post(self, request):
        transfer_id = request.data.get('transfer_id')

        if not transfer_id:
            return Response({"error": "transfer_id is required in the request body"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            transfer_instance = Transfer.objects.get(id=transfer_id)
            transfer_instance.status = 5
            transfer_instance.save()
            return Response({"message": "Transfer status changed "}, status=status.HTTP_200_OK)
        except Transfer.DoesNotExist:
            return Response({"error": "Transfer does not exist"}, status=status.HTTP_404_NOT_FOUND)


# To get the count of transfer initiated,completed,rejected ,cancelled -dashboard
class TransferStatusCountAPIView(APIView):
    """ Allows the DU head to get the number of transfers intiated ,
        completed,rejected and cancelled in his du"""

    permission_classes = [IsDuhead]

    def get(self, request):
        try:
            logged_in_duhead_du = self.request.user.employee_id.du.id
            transfer_count = {
                "Transfer initiated": Transfer.objects.filter(currentdu_id=logged_in_duhead_du, status__in=[1, 2]).count(),
                "Transfer completed": Transfer.objects.filter(currentdu_id=logged_in_duhead_du, status=3).count(),
                "Transfer rejected": Transfer.objects.filter(currentdu_id=logged_in_duhead_du, status=4).count(),
                "Transfer cancelled": Transfer.objects.filter(currentdu_id=logged_in_duhead_du, status=5).count(),
            }
            return Response(transfer_count, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"Something went wrong. {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
