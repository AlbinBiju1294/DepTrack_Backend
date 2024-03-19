# views.py
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime, timedelta
from rest_framework.views import APIView
from .serializers import TransferSerializer, TransferDetailsSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Transfer
from employee.models import Employee
from delivery_unit.models import DeliveryUnit
from .serializers import TransferSerializer, TransferDetailsSerializer, TransferAndDetailsSerializer, TransferAndEmployeeSerializer
from user.rbac import *
from rest_framework.pagination import LimitOffsetPagination
from .utils import prepare_email, send_email
import logging
from datetime import datetime


logger = logging.getLogger("django")


# saves the transfers initiated into the transfers and transfer details table
class CreateTransferAPIView(APIView):
    permission_classes = [IsPm | IsDuhead | IsAdmin]
    """The data is serialized using transfer serializer. If it is valid it is saved 
    into the transfer table. The transfer_id from the transfer instance is added 
    to the request data and then it is added to transfer details table along with
    other details"""

    def post(self, request):
        try:
            current_du_id = request.data.get('currentdu_id')
            target_du_id = request.data.get('targetdu_id')
            employee_id = request.data.get('employee_id')
            initiated_by = request.user.employee_id.id
            request.data['initiated_by'] = initiated_by
            request.data['total_experience'] = int(request.data['total_experience'])
            request.data['experion_experience'] = int(request.data['experion_experience'])

            if current_du_id == target_du_id and current_du_id != None and target_du_id != None:
                return Response({'error': 'Current and target DU cannot be the same.'}, status=status.HTTP_400_BAD_REQUEST)

            existing_transfer = Transfer.objects.filter(
                employee_id=employee_id).exclude(status__in=[3, 4, 5]).first()
            if existing_transfer:
                return Response({'error': 'Employee Transfer Already in Progress.'}, status=status.HTTP_400_BAD_REQUEST)
            transfer_serializer = TransferSerializer(data=request.data)

            if transfer_serializer.is_valid():
                transfer = transfer_serializer.save()
                request.data['transfer_id'] = transfer.id
                transfer_detail_serializer = TransferDetailsSerializer(data=request.data)
                if transfer_detail_serializer.is_valid():
                    transfer_detail_serializer.save()

                    #email logic
                    transfer_status = request.data.get('status')
                    initiated_by_emp = Employee.objects.get(id=initiated_by)
                    transfer_date_set = datetime.strptime(request.data.get('transfer_date'), "%Y-%m-%d")
                    
                    html_page = 'initiate_transfer_mail.html'
                    html_content_object = {
                        'user_name': request.user.employee_id.name,
                        'pm_name': initiated_by_emp.name,
                        'employee_number': transfer.employee_id.employee_number,
                        'employee_name':transfer.employee_id.name,
                        'transfer_id': transfer.id,
                        'current_du': transfer.currentdu_id.du_name,
                        'target_du': transfer.targetdu_id.du_name,
                        'transfer_date': transfer_date_set.strftime("%d-%m-%Y"),
                        'transfer_raised_on': transfer.transfer_raised_on.strftime("%d-%m-%Y")
                    }

                    subject= 'Transfer Initiated for '+ transfer.employee_id.employee_number
                                   
                    #checking if initiator is PM
                    if(transfer_status == 1):

                        email_parameters = prepare_email(transfer_status, current_du_id, target_du_id, html_page, html_content_object)  
                        send_email(subject=subject, recipient_to_email=email_parameters[0], recipient_cc_email=email_parameters[1], text_content=email_parameters[3], html_content=email_parameters[2])
                        return Response({'message': 'Transfer created and email sent successfully.'}, status=status.HTTP_201_CREATED)
                       
                    #checking if initiator is DU head
                    elif (transfer_status == 2):

                        email_parameters = prepare_email(transfer_status, current_du_id, target_du_id, html_page, html_content_object)  
                        send_email(subject=subject, recipient_to_email=email_parameters[0], recipient_cc_email=email_parameters[1], text_content=email_parameters[3], html_content=email_parameters[2])
                        return Response({'message': 'Transfer created and email sent successfully.'}, status=status.HTTP_201_CREATED)
                                            
                else:
                    transfer.delete()
                    return Response({'error': transfer_detail_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": transfer_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            logger.critical(e)
            return Response({"error": f"Transfer initiation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# view to get the whole details of the transfer by passing transfer id
class GetTransferDetailsAPIView(APIView):
    permission_classes = [IsPm | IsDuhead | IsAdmin ]
    """transfer id is extracted from the request body. Then the transfer instance is 
    obtained using the transfer id. Then the transfer details along with employee details
    is returned"""

    def get(self, request):
        try:
            transfer_id = request.query_params.get('transfer_id')
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
    """Query params are taken into a variable filter_params and based on those parameters 
    details are fetched from transfer table and the filtered content is returned as
    response"""

    permission_classes = [IsPm | IsDuhead | IsHrbp | IsAdmin]
    pagination_class = LimitOffsetPagination

    def get(self, request):
        try:
            filter_params = request.query_params
            query_set = Transfer.objects.filter(status__in=[3, 4, 5]).order_by('-id')
            
            if 'limit' in filter_params and 'offset' in filter_params:
                paginator = self.pagination_class()
                paginated = True
            else:
                paginated = False

            for key, value in filter_params.items():
                if key == 'employee_name':
                    query_set = query_set.filter(
                        employee_id__name__icontains=value)
                elif key == 'employee_number':
                    query_set = query_set.filter(
                        employee_id__employee_number__icontains=value)
                elif value and key not in ['start_date', 'end_date', 'offset', 'limit']:
                    query_set = query_set.filter(**{key: value})

            if 'start_date' in filter_params and 'end_date'  in filter_params:
                start_date = datetime.strptime(
                    filter_params['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(
                    filter_params['end_date'], '%Y-%m-%d').date()
                query_set = query_set.filter(
                    transfer_date__range=(start_date, end_date))

            if query_set.exists():
                if paginated:
                    paginator = self.pagination_class()
                    paginated_results = paginator.paginate_queryset(query_set, request)
                    serializer = TransferAndEmployeeSerializer(
                        paginated_results, many=True)
                    response_data = {
                        'count': paginator.count,
                        'next': paginator.get_next_link(),
                        'previous': paginator.get_previous_link(),
                        'results': serializer.data
                    }
                else:
                    serializer = TransferAndEmployeeSerializer(
                        query_set, many=True)
                    response_data = {'count': len(serializer.data), 'results': serializer.data}

                return Response({'data': response_data, 'message': 'Transfer history retrieved successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Transfer details do not exist.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Transfer History Listing API: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# to track the initiated transfer requests.
class GetInitiatedRequestsApiView(APIView):
    """transfer details are fetched where the du_id is same as that of the requestor
    and the status is either 1 or 2 which indicates initiated by PM or pending 
    approval"""

    permission_classes = [IsDuhead | IsAdmin | IsPm | IsHrbp]

    def get(self, request):
        try:
            du_id = request.query_params.get('du_id')
            if du_id == None:
                return Response({"error": "Provide Du id"}, status=status.HTTP_400_BAD_REQUEST)
            query_set = Transfer.objects.filter(
                Q(currentdu_id=du_id) & (Q(status=1) | Q(status=2))).order_by('-id')
            logger.info(query_set)
            if query_set:
                serializer = TransferAndEmployeeSerializer(query_set, many=True)
                return Response({"data": serializer.data,"message":"Initiated requests retreived successfully"}, status=status.HTTP_200_OK)
            return Response({"erroe": "Transfer details not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# To post the details when a request is approved by T-DU head
class ChangeApprovalDatePmAPIView(APIView):
    """
    When a target DU head views the detailed view of a transfer request, they can approve or reject it.
    If 'approve' is clicked then the transfer date can be changed and a new pm can be assigned. This data 
    is posted into the transfer table.
    """

    permission_classes = [IsDuhead | IsAdmin]

    def put(self, request):
        try:
            data = request.data
            transfer_id = data.get("transfer_id")
            new_pm = data.get("newpm_id")
            transfer_date = data.get("transfer_date")

            if(transfer_id == ' ' or transfer_date == ' ' or new_pm == ' '):
                return Response({'error': 'Provide the request data correctly.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                transfer = Transfer.objects.get(id=transfer_id)
            except Transfer.DoesNotExist as e:
                return Response({'error': f'Transfer details not found: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
            
            if new_pm:
                assigned_emp_pm =  Employee.objects.get(id=new_pm)
                transfer.newpm_id = assigned_emp_pm
            else:
                assigned_emp_pm = None
            transfer.status = 3
            transfer.transfer_date = transfer_date

            try:
                transferred_employee_id = transfer.employee_id.id
                transferred_employee_object = Employee.objects.get(id=transferred_employee_id)
            except Employee.DoesNotExist as e:
                return Response({'error': f'Employee not found: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
                
            transferred_employee_object.du_id = transfer.targetdu_id

            # Prepare email parameters
            transfer_date_set = datetime.strptime(transfer_date, "%Y-%m-%d")

            html_page = 'approval_mail.html'
            html_content_object = {
                'employee_number': transfer.employee_id.employee_number,
                'employee_name':transfer.employee_id.name,
                'transfer_id': transfer.id,
                'current_du': transfer.currentdu_id.du_name,
                'target_du': transfer.targetdu_id.du_name,
                'transfer_date': transfer_date_set.strftime("%d-%m-%Y"),
                'transfer_raised_on': transfer.transfer_raised_on.strftime("%d-%m-%Y"),
                'new_pm_id': assigned_emp_pm.name if new_pm else None
            }

            subject= 'Transfer Request Approved'
            
            current_du_id = transfer.currentdu_id
            target_du_id = transfer.targetdu_id
            transfer_status = transfer.status

            email_parameters = prepare_email(transfer_status, current_du_id, target_du_id, html_page, html_content_object, assigned_emp_pm)  

            transfer.save()
            transferred_employee_object.save()  

            send_email(subject=subject, recipient_to_email=email_parameters[0], recipient_cc_email=email_parameters[1], text_content=email_parameters[3], html_content=email_parameters[2])
                
            return Response({'message': 'Transfer date and PM changed successfully. Email sent successfully'}, status=status.HTTP_200_OK)            
            
        except Exception as e:
            return Response({'error': f'Error in changing the transfer date and PM: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#To approve a request by current DU head when the pm initiates the request         
class CDURequestApproval(APIView):
    """
    When a PM initiates a request current DU head can approve or reject it. If 'approve' is clicked then the 
    transfer date can be changed. This data is posted into the transfer table.
    """

    permission_classes = [IsDuhead | IsAdmin]

    def put(self, request):
        try:
            data = request.data
            transfer_id = data.get("transfer_id")
            transfer_date = data.get("transfer_date")

            if(transfer_id == ' ' or transfer_date == ' '):
                return Response({'error': 'Provide the request data correctly.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                transfer = Transfer.objects.get(id=transfer_id)
            except Transfer.DoesNotExist as e:
                return Response({'error': f'Transfer details not found: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)

            transfer.status = 2
            transfer.transfer_date = transfer_date

            try:
                transferred_employee_object = Employee.objects.get(id=transfer.employee_id.id)
            except Employee.DoesNotExist as e:
                return Response({'error': f'Employee not found: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
                

            # Prepare email parameters
            
            transfer_date_set = datetime.strptime(transfer_date, "%Y-%m-%d")

            html_page = 'initiate_transfer_mail.html'
            html_content_object = {
                'user_name': request.user.employee_id.name,
                'pm_name': transfer.initiated_by.name,
                'employee_number': transferred_employee_object.employee_number,
                'employee_name':transferred_employee_object.name,
                'transfer_id': transfer_id,
                'current_du': transfer.currentdu_id.du_name,
                'target_du': transfer.targetdu_id.du_name,
                'transfer_date': transfer_date_set.strftime("%d-%m-%Y"),
                'transfer_raised_on': transfer.transfer_raised_on.strftime("%d-%m-%Y")
             }
            subject= 'Transfer Initiated for '+ transfer.employee_id.employee_number
            current_du_id = transfer.currentdu_id
            target_du_id = transfer.targetdu_id
            transfer_status = transfer.status

            email_parameters = prepare_email(transfer_status, current_du_id, target_du_id, html_page, html_content_object)  

            transfer.save() 

            send_email(subject=subject, recipient_to_email=email_parameters[0], recipient_cc_email=email_parameters[1], text_content=email_parameters[3], html_content=email_parameters[2])
                
            return Response({'message': 'Transfer request approved by current DU head successfully. Email sent successfully'}, status=status.HTTP_200_OK)            
            

        except Exception as e:
            return Response({'error': f'Error in changing the transfer date: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       

# To list all the transfers that happened in a DU, in all statuses
class ListTransferHistoryAPIView(APIView):
    """
    Lists all the transfers that happened in a DU, both incoming and outgoing transfers. It takes details 
    from both the transfer table and employee table.
    """
    permission_classes = [IsAdmin | IsDuhead | IsPm | IsHrbp]
    pagination_class = LimitOffsetPagination

    def get(self, request):
        try:
            paginator = self.pagination_class()
            transfers = Transfer.objects.filter(status__in=[3,4,5]).order_by('-id')
            if transfers.exists():
                paginated_results = paginator.paginate_queryset(transfers, request)

                serializer = TransferAndEmployeeSerializer(paginated_results, many=True)

                response_data = {
                    'count': paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'results': serializer.data
                }


                if response_data:
                    return Response({'data': response_data, 'message': 'Transfer history retreived successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'List of transfer histories cannot be retreived.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Transfer details does not exists.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Transfer History Listing API: {e}")
            return Response({'error': {str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# To display all the pending approvals for a DU head.
class PendingApprovalsView(APIView):
    """
    To view all the pending transfer approval requests for a DU head both internal and external i.e., the requests
    initiated by PM which awaits the approval of DU head and the requests from another DU to accept an employee from
    their respective DU. 
    """
    permission_classes = [IsAuthenticated, IsDuhead | IsAdmin]

    def get(self, request):
        try:
            data = request.query_params
            du_id = int(data.get("du_id"))
            tab_switch_btn = int(data.get('tab_switch_btn'))

            if du_id == ' ' or tab_switch_btn == ' ':
                return Response({'error': 'Provide required data.'}, status=status.HTTP_200_OK)
            
            if tab_switch_btn == 1:     
                transfer_requests = Transfer.objects.filter(status=2, targetdu_id=du_id).order_by('-id')           #external=1                                       
                if not transfer_requests.exists():
                    return Response({"message": "No external requests from other DUs exists."}, status=status.HTTP_404_NOT_FOUND)

            elif tab_switch_btn == 2:                                                              #internal=2
                transfer_requests = Transfer.objects.filter(status=1, currentdu_id=du_id).order_by('-id') 
                if not transfer_requests.exists():
                    return Response({"message": "No internal requests from this DU exists."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "Invalid transfer tab request"}, status=status.HTTP_400_BAD_REQUEST)
            

            serializer = TransferAndEmployeeSerializer(transfer_requests, many=True)
            if serializer.data:
                return Response({'data': serializer.data, 'message':'Pending approvals retreived successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Error in retrieving pending approvals"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": {str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#To retreive the number of transfers happened in all DUs to display in dashboard
class NoOfTransfersInDUsAPIView(APIView):
    """
    It is for the dashboard to be displayed as a bar-graph. It retreives the number of transfers happened
    in th last 30 days in each DU.
    """
    permission_classes = [IsDuhead | IsHrbp | IsPm | IsAdmin]
 
    def get(self,request):
        try:
            thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
            dus = DeliveryUnit.objects.all()
            result_data=[]          
            for du in dus:
                try:
                    transfers_in_last_thirty_days = Transfer.objects.filter( Q(currentdu_id=du.id) | Q(targetdu_id=du.id), status = 3,
                                                                            transfer_date__gte=thirty_days_ago).count()                     
                except Transfer.DoesNotExist:
                    return Response({'error': 'DU transfer details not found.'}, status=status.HTTP_404_NOT_FOUND)
                result_data.append ({
                                        'du_name': du.du_name,
                                        'no_of_transfers': transfers_in_last_thirty_days
                                    })
            if result_data:
                return Response({'data':result_data, 'message':'Number of transfers in all dus retrieved successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Unable to retreive number of transfers in DUs'}, status=status.HTTP_404_NOT_FOUND)
       
        except Exception as e:
            return Response({'error':{str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


##To cancel the initiated transfer request by the duhead
class CancelTransfer(APIView):
    permission_classes = [IsDuhead]
    """The transfer status of a particular transfer_id is changed to
        the new status=5 in the transfer table which indicates that the
        transfer is cancelled.Done by the current_du head"""
 
    def post(self, request):
        transfer_id = request.data.get('transfer_id')
        try:
            if not transfer_id :
                return Response({"message": "transfer_id is required in the request body"}, status=status.HTTP_400_BAD_REQUEST)
            logged_in_duhead_du = self.request.user.employee_id.du_id.id
            transfer_instance = Transfer.objects.get(id=transfer_id)
            if transfer_instance.currentdu_id_id == logged_in_duhead_du:
                if transfer_instance.status not in [3, 4,5]:
                    transfer_instance.status = 5
                    transfer_instance.save()
                    return Response({"message": "Transfer status changed to cancel"}, status=status.HTTP_200_OK)
                elif transfer_instance.status == 3:
                    return Response({"message": "Cancellation is not allowed. Transfer has already been completed "},
                                status=status.HTTP_400_BAD_REQUEST)
                elif transfer_instance.status==4:
                     return Response({"message": "Cancellation is not allowed. Transfer has already been  rejected."},
                                status=status.HTTP_400_BAD_REQUEST)
                elif transfer_instance.status==5:
                     return Response({"message": "Cancellation is not allowed. Transfer has already been cancelled."},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Action not allowed. Employee does not belong to your Delivery Unit."},
                                status=status.HTTP_403_FORBIDDEN)
        except Transfer.DoesNotExist:
            return Response({"error": "Transfer does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({ "message": f"Something went wrong. {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


##To get the count of transfer initiated,completed,rejected ,cancelled -dashboard
class TransferStatusCountAPIView(APIView):
    """ Allows the DU head to get the number of transfers intiated ,
        completed,rejected and cancelled in his du"""
   
    permission_classes = [IsDuhead | IsAdmin | IsPm | IsHrbp]

    def get(self, request):
        try:
            thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
            logged_in_duhead_du = self.request.user.employee_id.du_id.id
            transfer_count = {
                "Transfer Initiated": Transfer.objects.filter(currentdu_id=logged_in_duhead_du, status__in=[1, 2], transfer_date__gte = thirty_days_ago ).count(),
                "Transfer Completed": Transfer.objects.filter(currentdu_id=logged_in_duhead_du,status=3, transfer_date__gte = thirty_days_ago).count(),
                "Transfer Rejected": Transfer.objects.filter(currentdu_id=logged_in_duhead_du,status=4, transfer_date__gte = thirty_days_ago).count(),
                "Transfer Cancelled": Transfer.objects.filter(currentdu_id=logged_in_duhead_du,status=5, transfer_date__gte = thirty_days_ago).count(),
            }
            return Response({"message":"transfer count display successful","data":transfer_count}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({ "error":str(e) }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#Change status for rejection of Transfer request
class TargetDURejectAPIView(APIView):
    """
    When a target DU head rejects the incoming request the transfer status and rejection reason must be edited  in
    the transfer table 
    """

    permission_classes = [IsDuhead|IsAdmin]
    
    def patch(self, request):
        try:
            data = request.data
            transfer_id = int(data.get("transfer_id"))
            rejection_reason=data.get("rejection_reason")
            if transfer_id and rejection_reason:
                 try:
                    transfer = Transfer.objects.get(id=transfer_id)
                 except  Transfer.DoesNotExist:
                    return Response({'error': 'Transfer does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                 transfer.status = 4
                 transfer.rejection_reason=rejection_reason
                 transfer.save()
                 return Response({ 'message': 'Transfer rejection status and reason updated '}, status=status.HTTP_200_OK)            
            else:
                return Response({"error":"Fields Missing"},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({ "errror": f"Something went wrong. {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 

            