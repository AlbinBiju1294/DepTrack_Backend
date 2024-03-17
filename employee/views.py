from django.shortcuts import render
from .models import *
from delivery_unit.models import *
from .serializers import EmployeeSerializer, DeliveryUnitMappingSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status, permissions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from .serializers import *
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework import generics, status, permissions
from user.rbac import *
from .forms import *
import pandas as pd
from user.models import *

# for pm listing
from rest_framework.response import Response
from user.models import User
from user.rbac import IsDuhead,IsAdmin
from .serializers import PmSerializer


# To list or create employee
class EmployeeListCreateView(ListCreateAPIView):
    """Allows the admin to list all the employees in the order of their
      employee_id.Details corresponding to all the fields of employee table
      is displayed.pagination is also applied"""
    permission_classes = (IsAdmin,)
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer

    pagination_class = LimitOffsetPagination

    def list(self, request, *args, **kwargs):

        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)

            if page is not None:

                serializer = self.get_serializer(page, many=True)
                res_data = {
                    'count': self.paginator.count,
                    'next': self.paginator.get_next_link(),
                    'previous': self.paginator.get_previous_link(),
                    'results': serializer.data
                }
                return Response(res_data, status=status.HTTP_200_OK)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response("Something went wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# To GET the list of Bands
class BandListView(ListCreateAPIView):
    """Extract the band levels from the band_level list so that the
      required band level can be selected by the DU or PM while filling form"""
    permission_classes=[IsDuhead|IsPm]
    def get(self, request):
        band_level = [("A1", "LEVEL1"), ("A2", "LEVEL2"),
                      ("B1", "LEVEL3"), ("B2", "LEVEL4"), ("C1", "LEVEL5")]
        band_levels = [band[0] for band in band_level]  
        return Response({"message": "Band levels retrieved successfully", "band_levels": band_levels}, status=status.HTTP_200_OK)    
    def post(self, request):
        return Response({"message":"Method \"POST\" not allowed."},status=status.HTTP_405_METHOD_NOT_ALLOWED)


# To list the new PM names in the C-DU
class PMListView(ListAPIView):
    """Lists the names and id of the PMs in the du so that the du head can select one Pm
      from this list for assigning to the new employee once the incoming transfer request
      is accepted.User objects are filtered for the condition user_role=2"""
    serializer_class = PmSerializer
    permission_classes = [IsDuhead | IsAdmin]
    pagination_class=None
    def get(self,request):
        try:
            logged_in_duhead_du = self.request.user.employee_id.du_id
            # pm_users = User.objects.filter(user_role=2, employee_id__du_id=logged_in_duhead_du)
            pm_users = User.objects.filter(user_role=2,employee_id__du_id=logged_in_duhead_du)

            if not pm_users:
                return Response({"message": "No Project Managers available "}, status=status.HTTP_404_NOT_FOUND)
           
            serializer = self.get_serializer(pm_users, many=True)
            return Response({ "message":"PM listing successful","data":serializer.data}, status=status.HTTP_200_OK)
 
        except Exception as ex:
            print(ex)
            return Response({"message": str(ex)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# View to search employee table
class EmployeeSearchListView(generics.ListAPIView):
    """
    Lists employess according to name or part of name in the search field and department of the logged in DU head
    """
    serializer_class = EmployeeSerializer
    permission_classes = [IsDuhead|IsAdmin|IsPm]
    pagination_class=None

    def list(self, request, *args, **kwargs):
        try:
            logged_in_user_department_id = self.request.user.employee_id.du_id.id
            name = self.request.query_params.get('name')
            if name is None or name =="":
                 return Response({"data": [], "message": "Employees Listed"}, status=status.HTTP_200_OK)
            queryset = Employee.objects.filter(du_id=logged_in_user_department_id, name__icontains=name)
            if  queryset.exists():
                serializer = self.get_serializer(queryset, many=True)
                return Response({"data": serializer.data, "message": "Employees Listed"}, status=status.HTTP_200_OK)
            else:
                return  Response({"data":[], "error": "No one matching search"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Internal Error"+str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DuHeadAndDuList(ListAPIView):
    """ Api endpoint to fetch  Du heads and currosponding Du's"""

    permission_classes = [IsAdmin]
    serializer_class = DuAndEmployeeSerializer
  

    def list(self, request, *args, **kwargs):
        try:
            queryset = DeliveryUnitMapping.objects
            if  queryset.exists():
                serializer = self.get_serializer(queryset, many=True)
                return Response({"data": serializer.data, "message": "DU heads Listed Successfully"}, status=status.HTTP_200_OK)
            else:
                return  Response({"data":[] , "error": "No DU heads"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Internal Error","error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateDUHeadAPIView(APIView):
    """
    It is a post request which enables the admin to change the DU head for a DU, this will be updated in the 
    DeliveryUnitMapping table.
    """
    permission_classes = [IsAdmin]

    def post(self, request):
        
        try:
            data = request.data
            new_du_head_id = data.get("du_head_id")
            du_id = data.get("du_id")

            try:
                du_head_emp_id = Employee.objects.get(id=new_du_head_id).id
                du_mapping_obj = DeliveryUnitMapping.objects.get(du_id=du_id)
            except Exception as e:
                print(e)
                return Response({'error': 'Error in retreiving employee and delivery unit mapping objects'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            du_mapping_obj.du_head_id = du_head_emp_id
            du_mapping_obj.save()
            return Response({'message': 'DU head updated successfully'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response({'error': 'DU head cannot be updated due to error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#view to process xl uploads 
class EmployeeUpdate(APIView):
    """Api endpoint to update Employee table from the uploaded xlsx file if employee is present updates department and designation 
    otherwise creates new employee instance  """

    permission_classes=(IsAdmin,)
    
    def post(self, request):
        try:
            form = ExcelUploadForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['file']
                df = pd.read_excel(excel_file) 
                for index, row in df.iterrows():
                    for column_name, cell_value in row.items():
                        if column_name.lower()=="email":
                            employee=Employee.objects.filter( mail_id=cell_value.strip()).first()
                            user=User.objects.filter(email=cell_value.strip()).first()
                            if(employee):
                                print(index,df.at[index,'role-id'])
                                if not pd.isna(df.at[index, 'role-id']) and df.at[index, 'role-id'] != '' and  not user:
                                    new_user = User(email=df.at[index,'email'],user_role=df.at[index,'role-id'],employee_id=employee,username=df.at[index,'user-name'])
                                    new_user.save()
                                new_du_id=df.at[index, 'department-id']
                                new_designation=df.at[index, 'designation']
                                delivery_unit_instance= DeliveryUnit.objects.get(id=new_du_id)
                                employee.du_id=delivery_unit_instance
                                employee.designation=new_designation
                                employee.save()
                            else:
                                delivery_unit_instance= DeliveryUnit.objects.get(id=new_du_id)
                                new_employee = Employee(employee_number=df.at[index,'employee-number'],name=df.at[index,'employee-name'], mail_id=df.at[index,'email'],designation=df.at[index,'designation'],du_id=delivery_unit_instance,profile_pic_path=df.at[index,'profile-pic'])
                                new_employee.save()
                                if not pd.isna(df.at[index, 'role-id']) and df.at[index, 'role-id'] != '':
                                    new_user = User(email=df.at[index,'email'],user_role=df.at[index,'role-id'],employee_id=new_employee,username=df.at[index,'user-name'])
                                    new_user.save()
                            
                return Response({'message': 'upload successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error':'upload failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as ex:
            return Response({'error':str(ex)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            print(str(ex))
        

class NoOfEmployeesInDUsAPIView(APIView):
    """
    Retrieves the number of employees in each DU
    """
    permission_classes = [IsDuhead | IsHrbp | IsPm | IsAdmin]
 
    def get(self,request):
        try:
            dus = DeliveryUnit.objects.all()
            result_data=[]          
            for du in dus:
                try:
                    employees_in_du = Employee.objects.filter(du_id = du.id).count()                     
                except Employee.DoesNotExist:
                    return Response({'error': 'Du employee details not found.'}, status=status.HTTP_404_NOT_FOUND)
                result_data.append ({
                                        'du_name': du.du_name,
                                        'no_of_employees': employees_in_du
                                    })
            if result_data:
                return Response({'data':result_data, 'message':'Number of employees in each dus retrieved successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Unable to retreive number of employees in DUs'}, status=status.HTTP_404_NOT_FOUND)
       
        except Exception as e:
            return Response({'error':{str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class PotentialDuHeads(ListAPIView):
    """List possible Du Candidates, users who have user role 1 and are not in the du mapping table"""
    
    permission_classes = [IsAdmin]
    def get(self, request):
        try:
            # Retrieve employee objects of users with role ID 1
            users_with_role_id_1 = User.objects.filter(user_role=1)
            employee_ids = [user.employee_id.id for user in users_with_role_id_1]
            employees = Employee.objects.filter(id__in=employee_ids)
            
            # Exclude employees who are already mapped as du heads 
            mapped_employee_ids = DeliveryUnitMapping.objects.values_list('du_head_id', flat=True)
            employees = employees.exclude(id__in=mapped_employee_ids)
            
            # Serialize the data and return the response
            data = [{'employee_id': emp.id, 'name': emp.name} for emp in employees]
            return Response({"data":data,"message":"du Head candidated listed"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PotentialHrbps(ListAPIView):


    permission_classes = [IsAdmin]
    def get(self, request):
        try:
            # Retrieve employee objects of users with role ID 4
            users_with_role_id_1 = User.objects.filter(user_role=4)
            employee_ids = [user.employee_id.id for user in users_with_role_id_1]
            employees = Employee.objects.filter(id__in=employee_ids)
            
            # Exclude employees who are already hrpbs of other du's
            mapped_employee_ids = DeliveryUnitMapping.objects.values_list('hrbp_id', flat=True)
            employees = employees.exclude(id__in=mapped_employee_ids)
            
            # Serialize the data and return the response
            data = [{'employee_id': emp.id, 'name': emp.name} for emp in employees]
            return Response({"data":data,"message":"hrbp Candidates Listed"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
