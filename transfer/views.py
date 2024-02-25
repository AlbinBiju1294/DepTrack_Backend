# views.py
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime, timedelta
from rest_framework.views import APIView
from .serializers import TransferSerializer, TransferDetailsSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Transfer, TransferDetails
from employee.models import Employee, DeliveryUnitMapping
from delivery_unit.models import DeliveryUnit
from .serializers import TransferSerializer, TransferDetailsSerializer, TransferAndDetailsSerializer, TransferAndEmployeeSerializer, TransferAndEmployeeSerializerTwo
from user.rbac import *
from rest_framework.pagination import LimitOffsetPagination


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
                request.data['transfer_id'] = transfer.id
                transfer_detail_serializer = TransferDetailsSerializer(
                    data=request.data)
                if transfer_detail_serializer.is_valid():
                    transfer_detail_serializer.save()
                    return Response({"status": True, 'message': 'Transfer created successfully.'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"status": False, 'message': transfer_detail_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
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
            print(e)
            return Response({'status': False, "message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# filters the transfers based on the given query parameters
class FilterTransfersAPIView(APIView):
    permission_classes = [IsPm | IsDuhead | IsHrbp]
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
                serializer = TransferAndEmployeeSerializerTwo(query_set, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"status": False, "message": "Transfers not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
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
                Q(currentdu_id=du_id) & (Q(status=1) | Q(status=2)))
            print(query_set)
            if query_set:
                serializer = TransferAndEmployeeSerializerTwo(query_set, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"message": "Transfer details not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            transfer_id = data.get("transfer_id")
            new_pm = data.get("newpm_id")
            targetdu_id = data.get("targetdu_id")
            transfer_date = data.get("transfer_date")

            if transfer_id == ' ' | new_pm == ' ' | targetdu_id == ' ':
                return Response({'message': 'Provide the request data correctly.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                transfer = Transfer.objects.get(id=transfer_id)
            except Transfer.DoesNotExist:
                return Response({'message': 'Transfer details not found.'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                assigned_emp_pm =  Employee.objects.get(id=new_pm)
            except Employee.DoesNotExist:
                return Response({'message': 'Employee not found.'}, status=status.HTTP_400_BAD_REQUEST)
            

            transfer.newpm_id = assigned_emp_pm.id
            transfer.transfer_date = transfer_date
            transfer.status = 3
            transfer.save()

            assigned_emp_pm.du_id = targetdu_id
            assigned_emp_pm.save()

            return Response({'message': 'Transfer date and pm changed successfully.'}, status=status.HTTP_200_OK)            

        except Exception as e:
            # logger(e)
            return Response({'message': f'Error in changing the transfer date and pm : {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

# To list all the transfers that happened in a DU, in all statuses 
class ListTransferHistoryAPIView(APIView):
    """
    Lists all the transfers that happened in a DU, both incoming and outgoing transfers. It takes details 
    from both the transfer table and employee table.
    """
    permission_classes = [IsAuthenticated, IsDuhead | IsPm | IsHrbp]
    pagination_class = LimitOffsetPagination

    def get(self, request):
        try:
            paginator = self.pagination_class()
            transfers = Transfer.objects.filter(status__in=[3,4,5]).order_by('-id')
            paginated_results = paginator.paginate_queryset(transfers, request)

            serializer = TransferAndEmployeeSerializer(paginated_results, many=True)

            response_data = {
                'count': paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'results': serializer.data
            }

            if response_data:
                return Response({'data': response_data}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Transfer history cannot be retreived.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            # logger.error(f"Transfer History Listing API: {e}")
            return Response({'message': f'Transfer history cannot be retreived: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

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
            data = request.data
            du_id = data.get("du_id")
            tab_switch_btn = data.get('tab_switch_btn')

            if du_id == ' ' | tab_switch_btn == ' ':
                return Response({'message': 'Provide required data.'}, status=status.HTTP_200_OK)
            
            if tab_switch_btn == 1:                                                                 #external=1                                       
                transfer_requests = Transfer.objects.filter(status=2, target_du=du_id)
            elif tab_switch_btn == 2:                                                               #internal=2
                transfer_requests = Transfer.objects.filter(status=1, current_du=du_id)

            serializer = TransferAndEmployeeSerializer(transfer_requests, many=True)
            if serializer.data:
                return Response({'data': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"message": f"Error in retreiving pending approvals: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": f"Error in retreiving pending approvals: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#To retreive the number of transfers happened in all DUs to display in dashboard
class NoOfTransfersInDUsAPIView(APIView):
    """
    It is for the dashboard to be displayed as a bar-graph. It retreives the number of transfers happened 
    in th last 30 days in each DU.
    """
    permission_classes = [IsDuhead | IsHrbp | IsPm | IsAdmin]

    def get(self,request):
        try:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            du_ids = DeliveryUnit.objects.all().values_list('du_id', flat=True) 
            result_data=[]          
            for du_id in du_ids:
                try:
                    transfers_in_last_thirty_days = Transfer.objects.filter( Q(currentdu_id=du_id) | Q(targetdu_id=du_id), status__in=[3],
                                                                        transfer_date__gte=thirty_days_ago).count()
                except Transfer.DoesNotExist:
                    return Response({'message': 'DU transfer details not found.'}, status=status.HTTP_400_BAD_REQUEST)
                
                result_data.append = {
                                        'du_id': du_id,
                                        'no_of_transfers': transfers_in_last_thirty_days
                                    }
                if result_data:
                    return Response({'data':result_data}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Unable to retreive number of transfers in a DU'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'message':'Error in fetching number of transfers in a DU: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


