from django.shortcuts import render
from .models import Employee
from .serializers import EmployeeSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListCreateAPIView


from rest_framework import generics, status, permissions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import OrderingFilter







# Create your views here.
class EmployeeListCreateView(ListCreateAPIView):
    permission_classes = (AllowAny,)
    queryset = Employee.objects.all().order_by('-id')
    serializer_class = EmployeeSerializer



    pagination_class = LimitOffsetPagination
    def list(self, request, *args, **kwargs):
        
        try:
            # access queryset from class level object
            queryset = self.get_queryset()
             # Accessing pagination class and generating paginated queryset
            page = self.paginate_queryset(queryset)

            if page is not None:
                # Generate Serialized data from query result if pagination, is applicable
                serializer = self.get_serializer(page, many=True)
                res_data = {
                    'count': self.paginator.count,
                    'next': self.paginator.get_next_link(),
                    'previous': self.paginator.get_previous_link(),
                    'results': serializer.data
                }
                return Response(res_data, status=status.HTTP_200_OK)

            # If paginator is not applicable return normal result
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            
            return Response("Something went wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



# class EmployeeSortView(generics.ListAPIView):
#     serializer_class=EmployeeSerializer
#     queryset=Employee.objects.all()
#     filter_backends=(DjangoFilterBackend,OrderingFilter)
#     ordering_fields=('name',)