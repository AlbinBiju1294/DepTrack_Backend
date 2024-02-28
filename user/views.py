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

# Create your views here.

# User registration view


class UserRegistrationView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                res_data = {"success": True, "message": "Registration Successful, Please Login",
                            "data": {"id": user.id, "username": user.username}}
                return Response(res_data, status=status.HTTP_201_CREATED)
            else:
                err_data = str(serializer.errors)
                res_data = {"success": False, "message": "Something went wrong", "data": {
                    "error": err_data}}
                return Response(res_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            res_data = {"success": False, "message": " Something went wrong !", "data": {
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



  




# #Api endpoint to get a single user
# class UserDetailsAPIView(RetrieveUpdateDestroyAPIView):
#     """ View gives details of a single user by primary key , 
#     and enables other  operations like  update user details, delete user details etc """

#     permission_classes = (IsAdmin,)
#     serializer_class = UserProfileSerializer
#     queryset = User.objects.filter(is_deleted=False).order_by('-id')
