from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, status, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import logging
from django.contrib.auth import update_session_auth_hash
from .serializers import *
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import UpdateAPIView, RetrieveUpdateAPIView, ListAPIView, GenericAPIView,RetrieveUpdateDestroyAPIView
from .rbac import IsDuhead, IsAdmin, IsHrbp, IsPm, IsUser
import logging

logger = logging.getLogger("django")

# Create your views here.

# User registration view


class UserRegistrationView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                res_data = {"message": "Registration Successful, Please Login",
                            "data": {"id": user.id, "username": user.username}}
                return Response(res_data, status=status.HTTP_201_CREATED)
            else:
                err_data = serializer.errors
                email_error = err_data.get('email', [])
                username_error = err_data.get('username', [])
                error_message = ''
                if email_error:
                    error_message = email_error[0]
                if username_error:
                    error_message = error_message+" "+username_error[0]
                logger.error(error_message)
                res_data = {"message": error_message}
                return Response(res_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            logger.error(ex, "on adding", request.data.username)
            res_data = {"message": " Something went wrong !", "data": {
                "error": str(ex)}, }
            return Response(res_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Api endpoint to List all users 
class UserListView(ListAPIView):
    """View gives list of all users in the User table to Admin level users """
    
    permission_classes = (IsAdmin,)         
    serializer_class =  UserProfileSerializer
    def list(self, request, *args, **kwargs):
        try:
            queryset = User.objects.filter(is_deleted=False).order_by('-id')
            if  queryset.exists():
                serializer = self.get_serializer(queryset, many=True)
                return Response({"data": serializer.data, "message": "Users Listed Successfully"}, status=status.HTTP_200_OK)
            else:
                return  Response({"data":[],"error": "Failed to retrieve Users"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Internal Error","error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SingleUserView(APIView):
    """View gives list of all users in the User table to Admin level users """
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            if user:
                return Response({'data':{
                    'id':user.id,
                    'username': user.username,
                    'email': user.email,
                    'role':user.user_role,
                    'du_id':user.employee_id.du_id.id
                }},status.HTTP_200_OK)
            else:
                return Response({"error":"User not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)},status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class SingleUserView(APIView):
    """View gives list of all users in the User table to Admin level users """
   
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        try:
            user = request.user
            if user:
                return Response({'data':{
                    'id':user.id,
                    'username': user.username,
                    'email': user.email,
                    'role':user.user_role
                }},status.HTTP_200_OK)
            else:
                return Response({"error":"User not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)},status.HTTP_500_INTERNAL_SERVER_ERROR)

  
class SingleUserView(APIView):
    """View gives list of all users in the User ta"ble to Admin level users """
   
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        try:
            user = request.user
            if user:
                return Response({'data':{
                    'id':user.id,
                    'username': user.username,
                    'email': user.email,
                    'role':user.user_role
                }},status.HTTP_200_OK)
            else:
                return Response({"error":"User not found"},status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)},status.HTTP_500_INTERNAL_SERVER_ERROR)