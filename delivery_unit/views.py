from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DeliveryUnit
from .serializers import DuSerializer
from rest_framework.permissions import IsAdminUser

# To add new Du 
class DeliveryUnitCreateAPIView(APIView):
    """Allows the admin to add new Du to the delivery_unit table.
       The Du_name is given in the body.If the entered Du already exists 
       then an error message will be displayed"""
    
    permission_classes = [IsAdminUser]
    def post(self, request):
        try:
            serializer = DuSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"new DU added successfully"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            res_data = {"message": " Something went wrong !", "data": {"error": str(e)}, }
            return Response(res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)













                # return Response({"status": True,"message":f"delivery unit{serializer.data} added successfully"}, status=status.HTTP_201_CREATED)
